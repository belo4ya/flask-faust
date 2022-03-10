import time
from http import HTTPStatus

from flask import Flask, url_for

from flask_faust import Faust, Task, TaskResult, Result

flask_config = {'SECRET_KEY': '1234'}
faust_config = {
    'FAUST_BOOTSTRAP_SERVER': 'localhost:9092',
    'FAUST_BACKEND_URL': r'D:\IT\Coding\Python Projects\flask-faust\store.db',
    'FAUST_CONCURRENCY': 2,
}

app = Flask(__name__)
app.config.from_mapping({**flask_config, **faust_config})

faust = Faust(app)
faust_app = faust.get_faust_app()


@faust.task('tasks-topic')
class HelloWorldTask(Task):

    def handle(self) -> Result:
        print(f'Task started: task_id={self.task_id}')
        time.sleep(4)
        print(f'Task done: task_id={self.task_id}')
        return Result(data=f'Hello, {self.data["name"]}')


@app.get('/tasks/')
def task_view():
    task_id = HelloWorldTask.send({'name': 'Alexey'})
    status_url = url_for('task_status_view', task_id=task_id)
    response = {'task_id': task_id}
    headers = {'Location': status_url}
    return response, HTTPStatus.ACCEPTED, headers


@app.get('/tasks/<task_id>/')
def task_status_view(task_id: str):
    result = TaskResult(task_id)
    response = {'task_id': task_id, 'status': result.status}
    if not result.ready():
        return response | {'result': None, 'meta': result.meta}

    return response | {'result': result.result, 'meta': None}


if __name__ == '__main__':
    app.run(debug=True)
