import gevent
import gevent.pool
import os
import signal
import datetime
import time
import socket
import traceback
import psutil
import sys
import pymongo
from bson import ObjectId
from gevent.pywsgi import WSGIServer

from .job import Job
from .exceptions import JobTimeoutException, StopRequested, JobInterrupt
from .context import set_current_worker, set_current_job, get_current_job, connections, enable_greenlet_tracing
from .queue import Queue

# https://groups.google.com/forum/#!topic/gevent/EmZw9CVBC2g
# if "__pypy__" in sys.builtin_module_names:
#   def _reuse(self):
#       self._sock._reuse()
#   def _drop(self):
#       self._sock._drop()
#   gevent.socket.socket._reuse = _reuse
#   gevent.socket.socket._drop = _drop


class Worker(object):
  """ Main worker class. """

  # Allow easy overloading
  job_class = Job

  # Valid statuses:
  #       * init: General worker initialization
  #       * wait: Waiting for new jobs from Redis (BLPOP in progress)
  #       * spawn: Got some new jobs, greenlets are being spawned
  #       * full: All the worker pool is busy executing jobs
  #       * join: Waiting for current jobs to finish, no new one will be accepted
  #       * kill: Killing all current jobs
  #       * stop: Worker is stopped, no jobs should remain
  status = "init"

  mongodb_jobs = None
  mongodb_logs = None
  redis = None

  def __init__(self, config):

    self.config = config

    set_current_worker(self)

    if self.config.get("trace_greenlets"):
      enable_greenlet_tracing()

    self.datestarted = datetime.datetime.utcnow()
    self.queues = [x for x in self.config["queues"] if x]
    self.done_jobs = 0
    self.max_jobs = self.config["max_jobs"]

    self.connected = False  # MongoDB + Redis

    self.exitcode = 0
    self.process = psutil.Process(os.getpid())
    self.greenlet = gevent.getcurrent()

    self.id = ObjectId()
    if config["name"]:
      self.name = self.config["name"]
    else:
      self.name = self.make_name()

    self.pool_size = self.config["gevent"]

    from .logger import LogHandler
    self.log_handler = LogHandler(quiet=self.config["quiet"])
    self.log = self.log_handler.get_logger(worker=self.id)

    self.log.info("Starting Gevent pool with %s worker greenlets (+ 1 monitoring)" % self.pool_size)

    self.gevent_pool = gevent.pool.Pool(self.pool_size)

    # Keep references to main greenlets
    self.greenlets = {}

  def connect(self, force=False):

    if self.connected and not force:
      return

    # Accessing connections attributes will automatically connect
    self.redis = connections.redis
    self.mongodb_jobs = connections.mongodb_jobs

    if self.config["mongodb_logs"] == "0":
      self.log_handler.set_collection(False)  # Disable
    else:
      self.mongodb_logs = connections.mongodb_logs
      self.log_handler.set_collection(self.mongodb_logs.mrq_logs)

    self.connected = True

    # Be mindful that this is done each time a worker starts
    self.ensure_indexes()

  def ensure_indexes(self):

    if self.mongodb_logs:

      self.mongodb_logs.mrq_logs.ensure_index([("job", 1)], background=False)
      self.mongodb_logs.mrq_logs.ensure_index([("worker", 1)], background=False, sparse=True)

    self.mongodb_jobs.mrq_workers.ensure_index([("status", 1)], background=False)
    self.mongodb_jobs.mrq_workers.ensure_index([("datereported", 1)], background=False, expireAfterSeconds=3600)

    self.mongodb_jobs.mrq_jobs.ensure_index([("status", 1)], background=False)
    self.mongodb_jobs.mrq_jobs.ensure_index([("path", 1), ("status", 1)], background=False)
    self.mongodb_jobs.mrq_jobs.ensure_index([("worker", 1), ("status", 1)], background=False, sparse=True)
    self.mongodb_jobs.mrq_jobs.ensure_index([("queue", 1), ("status", 1)], background=False)
    self.mongodb_jobs.mrq_jobs.ensure_index([("dateexpires", 1)], sparse=True, background=False, expireAfterSeconds=0)

    self.mongodb_jobs.mrq_scheduled_jobs.ensure_index([("hash", 1)], unique=True, background=False, drop_dups=True)

    try:
      # This will be default in MongoDB 2.6
      self.mongodb_jobs.command({"collMod": "mrq_jobs", "usePowerOf2Sizes": True})
      self.mongodb_jobs.command({"collMod": "mrq_workers", "usePowerOf2Sizes": True})
    except:
      pass

  def make_name(self):
    """ Generate a human-readable name for this worker. """
    return "%s.%s" % (socket.gethostname().split(".")[0], os.getpid())

  def greenlet_scheduler(self):

    from .scheduler import Scheduler
    scheduler = Scheduler(self.mongodb_jobs.mrq_scheduled_jobs)

    scheduler.sync_tasks(self.config.get("scheduler_tasks") or [])

    while True:
      scheduler.check()
      time.sleep(int(self.config["scheduler_interval"]))

  def greenlet_monitoring(self):
    """ This greenlet always runs in background to update current status in MongoDB every 10 seconds.

    Caution: it might get delayed when doing long blocking operations. Should we do this in a thread instead?
     """

    while True:

      # print "Monitoring..."

      self.report_worker()
      self.flush_logs(w=0)
      time.sleep(int(self.config["report_interval"]))

  def get_memory(self):
    return self.process.get_memory_info().rss

  def get_worker_report(self):

    greenlets = []

    for greenlet in self.gevent_pool:
      g = {}
      short_stack = []
      stack = traceback.format_stack(greenlet.gr_frame)
      for s in stack[1:]:
        if "/gevent/hub.py" in s:
          break
        short_stack.append(s)
      g["stack"] = short_stack

      job = get_current_job(id(greenlet))
      if job:
        if job.data:
          g["path"] = job.data["path"]
        g["datestarted"] = job.datestarted
        g["id"] = job.id
        g["time"] = getattr(greenlet, "_trace_time", 0)
        g["switches"] = getattr(greenlet, "_trace_switches", None)
        if self.config["trace_mongodb"]:
          g["mongodb"] = dict(job._trace_mongodb)
      greenlets.append(g)

    cpu = self.process.get_cpu_times()

    # Avoid sharing passwords or sensitive config!
    whitelisted_config = [
      "max_jobs",
      "gevent",
      "processes",
      "queues",
      "scheduler",
      "name",
      "local_ip"
    ]

    return {
      "status": self.status,
      "config": {k: v for k, v in self.config.iteritems() if k in whitelisted_config},
      "done_jobs": self.done_jobs,
      "datestarted": self.datestarted,
      "datereported": datetime.datetime.utcnow(),
      "name": self.name,
      "process": {
        "pid": self.process.pid,
        "cpu": {
          "user": cpu.user,
          "system": cpu.system,
          "percent": self.process.get_cpu_percent(0)
        },
        "mem": {
          "rss": self.get_memory()
        }
        # https://code.google.com/p/psutil/wiki/Documentation
        # get_open_files
        # get_connections
        # get_num_ctx_switches
        # get_num_fds
        # get_io_counters
        # get_nice
      },
      "jobs": greenlets
    }

  def report_worker(self, w=0):

    try:
      self.mongodb_jobs.mrq_workers.update({
        "_id": ObjectId(self.id)
      }, {"$set": self.get_worker_report()}, upsert=True, w=w)
    except pymongo.errors.AutoReconnect:
      self.log.debug("Worker report failed.")

  def greenlet_admin(self):
    """ This greenlet is used to get status information about the worker when --admin_port was given
    """

    if self.config["processes"] > 1:
      self.log.debug("Admin server disabled because of multiple processes.")
      return

    from flask import Flask
    from mrq.dashboard.utils import jsonify
    app = Flask("admin")

    @app.route('/')
    def route_index():
      report = self.get_worker_report()
      report.update({
        "_id": self.id
      })
      return jsonify(report)

    self.log.debug("Starting admin server on port %s" % self.config["admin_port"])
    try:
      server = WSGIServer(("0.0.0.0", self.config["admin_port"]), app, log=open(os.devnull, "w"))
      server.serve_forever()
    except Exception, e:
      self.log.debug("Error in admin server : %s" % e)

  def flush_logs(self, w=0):
    self.log_handler.flush(w=w)

  def work_loop(self):
    """Starts the work loop.

    """

    self.connect()

    self.status = "started"

    self.greenlets["monitoring"] = gevent.spawn(self.greenlet_monitoring)

    if self.config["scheduler"]:
      self.greenlets["scheduler"] = gevent.spawn(self.greenlet_scheduler)

    if self.config["admin_port"]:
      self.greenlets["admin"] = gevent.spawn(self.greenlet_admin)

    self.install_signal_handlers()

    has_raw = any(q.is_raw or q.is_sorted for q in [Queue(x) for x in self.queues])

    try:

      while True:

        while True:

          free_pool_slots = self.gevent_pool.free_count()

          if free_pool_slots > 0:
            self.status = "wait"
            break
          self.status = "full"
          gevent.sleep(0.01)

        self.log.info('Listening on %s' % self.queues)

        # worker.status will be set to "spawn" as soon as we're not waiting anymore.
        jobs = Queue.dequeue_jobs(self.queues, max_jobs=free_pool_slots, job_class=self.job_class, worker=self)

        for job in jobs:

          # TODO investigate spawn_raw?
          self.gevent_pool.spawn(self.perform_job, job)

        if self.max_jobs and self.max_jobs >= self.done_jobs:
          self.log.info("Reached max_jobs=%s" % self.done_jobs)
          break

        # We seem to have exhausted available jobs, we can sleep for a while.
        if has_raw and len(jobs) < free_pool_slots:
          self.status = "wait"
          gevent.sleep(1)

    except StopRequested:
      pass

    finally:

      try:

        self.log.debug("Joining the greenlet pool...")
        self.status = "join"

        self.gevent_pool.join(timeout=None, raise_error=False)
        self.log.debug("Joined.")

      except StopRequested:
        pass

      self.status = "kill"

      self.gevent_pool.kill(exception=JobInterrupt, block=True)

      for g in self.greenlets:
        g_time = getattr(self.greenlets[g], "_trace_time", 0)
        g_switches = getattr(self.greenlets[g], "_trace_switches", None)
        self.greenlets[g].kill(block=True)
        self.log.debug("Greenlet for %s killed (%0.5fs, %s switches)." % (g, g_time, g_switches))

      self.status = "stop"

      self.report_worker(w=1)
      self.flush_logs(w=1)

      g_time = getattr(self.greenlet, "_trace_time", 0)
      g_switches = getattr(self.greenlet, "_trace_switches", None)
      self.log.debug("Exiting main worker greenlet (%0.5fs, %s switches)." % (g_time, g_switches))

    return self.exitcode

  def perform_job(self, job):
    """ Wraps a job.perform() call with timeout logic and exception handlers.

        This is the first call happening inside the greenlet.
    """

    if self.config["trace_memory"]:
      job.trace_memory_start()

    set_current_job(job)

    gevent_timeout = gevent.Timeout(job.timeout, JobTimeoutException(
      'Gevent Job exceeded maximum timeout value (%d seconds).' % job.timeout
    ))

    gevent_timeout.start()

    try:
      job.perform()

    except job.retry_on_exceptions:
      self.log.error("Caught exception => retry")
      job.save_retry(sys.exc_info()[1], exception=True)

    except job.cancel_on_exceptions:
      self.log.error("Job cancelled")
      job.save_status("cancel", exception=True)

    except JobTimeoutException:
      if job.task.cancel_on_timeout:
        self.log.error("Job timeouted after %s seconds, cancelled" % job.timeout)
        job.save_status("cancel", exception=True)
      else:
        self.log.error("Job timeouted after %s seconds" % job.timeout)
        job.save_status("timeout", exception=True)

    except JobInterrupt:
      job.save_status("interrupt", exception=True)

    except Exception:
      job.save_status("failed", exception=True)

    finally:
      gevent_timeout.cancel()
      set_current_job(None)

      self.done_jobs += 1

      if self.config["trace_memory"]:
        job.trace_memory_stop()

  def shutdown_graceful(self):
    """ Graceful shutdown: waits for all the jobs to finish. """

    # This is in the 'exitcodes' list in supervisord so processes
    # exiting gracefully won't be restarted.
    self.exitcode = 2

    self.log.info("Graceful shutdown...")
    raise StopRequested()

  def shutdown_now(self):
    """ Forced shutdown: interrupts all the jobs. """

    # This is in the 'exitcodes' list in supervisord so processes
    # exiting gracefully won't be restarted.
    self.exitcode = 3

    self.log.info("Forced shutdown...")
    self.status = "killing"

    self.gevent_pool.kill(exception=JobInterrupt, block=False)

    raise StopRequested()

  def install_signal_handlers(self):
    """ Handle events like Ctrl-C from the command line. """

    self.graceful_stop = False

    def request_shutdown_now():
      self.shutdown_now()

    def request_shutdown_graceful():

      # Second time CTRL-C, shutdown now
      if self.graceful_stop:
        request_shutdown_now()
      else:
        self.graceful_stop = True
        self.shutdown_graceful()

    # First time CTRL-C, try to shutdown gracefully
    gevent.signal(signal.SIGINT, request_shutdown_graceful)

    # User (or Heroku) requests a stop now, just mark tasks as interrupted.
    gevent.signal(signal.SIGTERM, request_shutdown_now)

