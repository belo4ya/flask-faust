# Flask-Faust

Flask extension for background tasks using Kafka and Faust

## Usage

### Simple Usage

Create a Flask app like you always have. Add several configuration parameters to the application. Create a `Faust`
object.

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
```

Inherit your task class from `Task` and implement the `handle` method in it. Using the `Faust.task` decorator register
your task class and assign it to the Kafka topic.

```py
@faust.task('tasks-topic')
class SimpleTask(Task):

    def handle(self) -> Result | None:
        ...
```

Use the `send` method to send your task to the task queue. With the help of task ID and the `TaskResult` class, you can
get to the result of the task execution.

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

To start the worker, use the command below or refer to the
Faust [documentation](https://github.com/faust-streaming/faust)

```shell
faust -A module.faust_app worker -l info
```
