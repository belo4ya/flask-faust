from __future__ import annotations

from datetime import datetime

import peewee as pw
from playhouse.fields import PickleField
from playhouse.sqlite_ext import JSONField

from flask_faust import status


class BaseModel(pw.Model):
    pass


class TaskModel(BaseModel):
    task_id = pw.CharField(155, unique=True)
    status = pw.CharField(50, default=status.PENDING)
    result = PickleField(null=True)
    meta = JSONField(null=True)
    date_arrival = pw.DateTimeField(default=datetime.utcnow)
    date_done = pw.DateTimeField(default=datetime.utcnow)
    traceback = pw.TextField(null=True)

    def save(self, *args, **kwargs) -> bool | int:
        self.date_done = datetime.utcnow()
        return super(TaskModel, self).save(*args, **kwargs)


def create_tables(db_url: str) -> None:
    db = pw.SqliteDatabase(db_url)
    # noinspection PyProtectedMember
    TaskModel._meta.database = db

    if not TaskModel.table_exists():
        db.create_tables([TaskModel])
