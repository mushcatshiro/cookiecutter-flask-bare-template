from flask import (
    Flask,
    jsonify
)
{% if cookiecutter.requires_async_task == 'true' %}  # noqa
from celery import Celery
{% endif %}  # noqa
{% if cookiecutter.requires_database_setup == 'true' %}  # noqa
from flask_sqlalchemy import SQLAlchemy
{% endif %}  # noqa


app = Flask(__name__)
app.config['SECRET_KEY'] = 'R4nD0mS3cre7'
{% if cookiecutter.requires_database_setup == 'true' %}  # noqa
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////{{cookiecutter.database_name}}.sqlite'  # noqa
db = SQLAlchemy(app)
{% endif %}  # noqa

{% if cookiecutter.requires_async_task == 'true' %}  # noqa
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
    {{cookiecutter.async_task_function}}  # noqa
    return
{% endif %}  # noqa


@app.route('/{{cookiecutter.endpoint_name}}')
def {{cookiecutter.endpoint_name}}():  # noqa
    {{cookiecutter.endpoint_function}}  # noqa
    return jsonify(resp)


{% if cookiecutter.requires_async_task == 'true' %}  # noqa
@app.route('/{{cookiecutter.endpoint_name}}/status/<string:task_id>')  # noqa
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
{% endif %}  # noqa


if __name__ == '__main__':
    # create db if DNE?
    app.run()
