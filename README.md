# Flask-Faust

Simple task queues with Kafka and Faust

## Usage

### Simple Usage

```py
from flask import Flask

from flask_faust import Faust, Task, TaskResult, Result

flask_config = {}
faust_config = {
    'FAUST_BOOTSTRAP_SERVER': 'localhost:9092',
    'FAUST_BACKEND_URL': 'store.db',
}

app = Flask(__name__)
app.config.from_mapping({**flask_config, **faust_config})

faust = Faust(app)
faust_app = faust.get_faust_app()


@faust.task('tasks-topic')
class SimpleTask(Task):

    def handle(self) -> Result | None:
        ...
```

```py
@faust.task('tasks-topic')
class SimpleTask(Task):

    def handle(self) -> Result | None:
        ...
```

```py
@app.get('/tasks/')
def task_view():
    task_id = SimpleTask.send(...)
    ...


@app.get('/tasks/<task_id>/')
def task_status_view(task_id: str):
    result = TaskResult(task_id)
    ...
```

```shell
faust -A filename.faust_app worker -l info
```
