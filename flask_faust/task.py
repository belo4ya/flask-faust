from __future__ import annotations

import abc
from datetime import datetime
from typing import Any

from pydantic import BaseModel

from flask_faust import status
from flask_faust.models import TaskModel
from flask_faust.producer import BaseProducer


def _get_task(task_id: str) -> TaskModel:
    return TaskModel.get(task_id=task_id)


class Task(abc.ABC):
    task_id: str
    data: Any

    def __init__(self, task_id: str, data: Any):
        self.task_id = task_id
        self.data = data
        TaskModel.create(task_id=task_id)

    def __call__(self) -> None:
        try:
            self._start()
            result = self.handle()
            self._success(result)
        except Exception as e:
            self.fail(e)

    @abc.abstractmethod
    def handle(self) -> Result | None:
        pass

    def update_state(self, meta: Meta) -> None:
        task = _get_task(self.task_id)
        task.meta = meta.dict()
        task.save()

    def fail(self, exc: Exception = None) -> None:
        task = _get_task(self.task_id)
        task.status = status.FAILURE
        if exc:
            task.traceback = f'{type(exc)}: {exc}'

        task.save()

    def _start(self) -> None:
        task = _get_task(self.task_id)
        task.status = status.STARTED
        task.save()

    def _success(self, result: Result = None) -> None:
        task = _get_task(self.task_id)
        task.status = status.SUCCESS
        if result:
            task.result = result.data
            if result.meta:
                task.meta = result.meta.dict()

        task.save()


class Result(BaseModel):
    data: Any
    meta: Meta | None = None


class Meta(BaseModel):
    pass


class TaskResult:

    def __init__(self, task_id: str):
        self._task = _get_task(task_id)

        self._task_id = self._task.task_id
        self._status = self._task.status

        self._result = self._task.result
        self._meta = Meta(**self._task.meta) if self._task.meta else None

        self._date_arrival = self._task.date_arrival
        self._date_done = self._task.date_done
        self._traceback = self._task.traceback

    @property
    def task_id(self) -> str:
        return self._task_id

    @property
    def status(self) -> str:
        return self._status

    @property
    def result(self) -> Any:
        return self._result

    @property
    def meta(self) -> Meta | None:
        return self._meta

    @property
    def date_arrival(self) -> datetime:
        return self._date_arrival

    @property
    def date_done(self) -> datetime:
        return self._date_done

    @property
    def traceback(self) -> str:
        return self._traceback

    def ready(self) -> bool:
        return self._status in status.READY_STATUSES

    def successful(self) -> bool:
        return self._status == status.SUCCESS

    def failed(self) -> bool:
        return self._status == status.FAILURE


class TaskSender:

    def __init__(self, producer: BaseProducer, topic: str):
        self._producer = producer
        self._topic = topic

    def send(self, data: Any) -> str:
        return self._producer.send(self._topic, data)
