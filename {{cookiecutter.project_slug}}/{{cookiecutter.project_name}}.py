from flask import (
    Flask,
    jsonify
)
from flask.logging import default_handler
import logging
import logging.handlers
import os
{% if cookiecutter.requires_async_task == 'true' %}
from celery import Celery
{% endif %}
{% if cookiecutter.requires_database_setup == 'true' %}
from flask_sqlalchemy import SQLAlchemy
{% endif %}


app = Flask(__name__)
app.config['SECRET_KEY'] = 'R4nD0mS3cre7'

app.logger.removeHandler(default_handler)
logfile_handler = logging.handlers.RotatingFileHandler(
    filename=os.path.join(os.getcwd(), "{{cookiecutter.project_name}}.log"),
    maxBytes=10000,
    backupCount=10
)
app.logger.addHandler(logfile_handler)

{% if cookiecutter.requires_database_setup == 'true' %}
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////{{cookiecutter.database_name}}.sqlite'
db = SQLAlchemy(app)
{% endif %}


{% if cookiecutter.requires_async_task == 'true' %}
def make_celery(app):
    celery = Celery(
        __name__,
        backend='db+sqlite:///{{cookiecutter.async_task_db_name}}.sqlite',
        # backend='redis://localhost:6379/0',
        broker='{{cookiecutter.async_task_message_broker_uri}}'
    )
    db.init_app(app)
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


celeryapp = make_celery(app)


@celeryapp.task
def long_task(x_pred):
    {{cookiecutter.async_task_function}}
    return
{% endif %}


@app.route('/{{cookiecutter.endpoint_name}}')
def {{cookiecutter.endpoint_name}}():
    {{cookiecutter.endpoint_function}}
    return jsonify(resp)


{% if cookiecutter.requires_async_task == 'true' %}
@app.route('/{{cookiecutter.endpoint_name}}/status/<string:task_id>')
def status(task_id):
    task = long_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']

            response['result_scatter'] =\
                [[i, j] for i, j in zip(task.info['result']['x_pred'],
                                        task.info['result']['y_pred'])]
    else:
        response = {
            'state': task.state,
            'status': str(task.info),  # this is the exception raised
        }
    return render_template('status.html', response=response)
{% endif %}


if __name__ == '__main__':
    # create db if DNE?
    app.run()
