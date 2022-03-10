import abc
import json
import uuid
from typing import Any

from confluent_kafka import SerializingProducer
from confluent_kafka.serialization import SerializationContext


class BaseProducer(abc.ABC):

    @abc.abstractmethod
    def send(self, topic: str, data: Any) -> str:
        pass


class DefaultProducer(BaseProducer):

    def __init__(self, bootstrap_server: str, timeout: int = None):
        self._producer = SerializingProducer({
            'bootstrap.servers': bootstrap_server,
            'value.serializer': _json_serialize
        })
        self._timeout = timeout

    def send(self, topic: str, data: Any) -> str:
        task_id = _uuid()
        self._producer.produce(topic, value={'task_id': task_id, 'data': data})
        self._producer.flush(self._timeout)
        return task_id


def _json_serialize(obj: Any, _: SerializationContext) -> bytes:
    return json.dumps(obj).encode('utf-8')


def _uuid() -> str:
    return str(uuid.uuid4())
