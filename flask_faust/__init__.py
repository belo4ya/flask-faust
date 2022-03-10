from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Type, Callable

import faust
from flask import Flask

from flask_faust.models import create_tables
from flask_faust.producer import DefaultProducer, BaseProducer
from flask_faust.task import Task, TaskSender, TaskResult, Result, Meta

__all__ = [
    'Faust',
    'Task',
    'TaskResult',
    'Result',
    'Meta',
]


class Faust:
    _app: Flask
    _faust: _faust.App
    _producer: BaseProducer
    _concurrency: int
    _pool: ThreadPoolExecutor

    def __init__(self, app: Flask = None):
        if app:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        self._app = app
        self._app.extensions['faust_ext'] = self

        bootstrap_server = app.config['FAUST_BOOTSTRAP_SERVER']
        backend_url = app.config['FAUST_BACKEND_URL']
        concurrency = app.config.get('FAUST_CONCURRENCY', 1)
        timeout = app.config.get('FAUST_PRODUCER_TIMEOUT', -1)

        self._faust = faust.App(app.name + '-faust', broker=bootstrap_server)
        self._producer = DefaultProducer(bootstrap_server, timeout=timeout)

        self._concurrency = concurrency
        self._pool = ThreadPoolExecutor(self._concurrency, initializer=app.app_context().push)

        create_tables(backend_url)

    def get_faust_app(self) -> faust.App:
        return self._faust

    def task(self, topic_name: str) -> Callable[[Type[Task]], TaskSender]:

        def _task(task_cls: Type[Task]) -> TaskSender:
            async def agent(stream):
                async for event in stream:
                    task = task_cls(event['task_id'], event['data'])
                    try:
                        self._faust.loop.run_in_executor(self._pool, task)
                    except Exception as e:
                        task.fail(e)

            agent.__name__ = f'{agent.__name__}__{topic_name}'
            topic = self._faust.topic(topic_name)
            self._faust.agent(topic, concurrency=self._concurrency)(agent)
            return TaskSender(self._producer, topic_name)

        return _task
