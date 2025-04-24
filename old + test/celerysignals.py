# celery_signals.py

from celery.signals import task_prerun, task_postrun, task_failure
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import FlowerTask  # renamed model
import os

# Load your PostgreSQL URI from environment variable
POSTGRES_URI = os.getenv("POSTGRES_URI")

engine = create_engine(POSTGRES_URI)
Session = sessionmaker(bind=engine)

task_start_times = {}  # temporarily store start times by task_id

@task_prerun.connect
def task_started_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **extras):
    task_start_times[task_id] = datetime.utcnow()
    session = Session()
    log = FlowerTask(
        task_id=task_id,
        name=sender.name,
        args=str(args),
        kwargs=str(kwargs),
        status="STARTED",
        started_at=task_start_times[task_id],
    )
    session.merge(log)
    session.commit()
    session.close()

@task_postrun.connect
def task_finished_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, **extras):
    ended_at = datetime.utcnow()
    started_at = task_start_times.pop(task_id, ended_at)
    runtime = (ended_at - started_at).total_seconds()

    session = Session()
    log = session.get(FlowerTask, task_id)
    if log:
        log.status = "SUCCESS"
        log.ended_at = ended_at
        log.runtime = runtime
        log.result = str(retval)
        session.commit()
    session.close()

@task_failure.connect
def task_failed_handler(sender=None, task_id=None, exception=None, args=None, kwargs=None, traceback=None, **extras):
    ended_at = datetime.utcnow()
    started_at = task_start_times.pop(task_id, ended_at)
    runtime = (ended_at - started_at).total_seconds()

    session = Session()
    log = session.get(FlowerTask, task_id)
    if log:
        log.status = "FAILED"
        log.ended_at = ended_at
        log.runtime = runtime
        log.exception = str(exception)
        log.traceback = str(traceback)
        session.commit()
    session.close()
