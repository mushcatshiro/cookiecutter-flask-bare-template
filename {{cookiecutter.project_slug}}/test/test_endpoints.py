from {{cookiecutter.project_slug}}.{{cookiecutter.project_name}} import (
    app,
    {% if cookiecutter.requires_database_setup == 'true' %}
    db
    {% endif %}
)
import unittest
import json


class FlaskApiAPITest(unittest.TestCase):
    """docstring for FlaskAPITest"""

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        {% if cookiecutter.requires_database_setup == 'true' %}
        db.create_all()
        {% endif %}
        self.client = self.app.test_client()

    def tearDown(self):
        {% if cookiecutter.requires_database_setup == 'true' %}
        db.session.remove()
        db.drop_all()
        {% endif %}
        self.app_context.pop()

    def test_api_{{cookiecutter.endpoint_name}}(self):
        response = self.client.get('/{{cookiecutter.endpoint_name}}')
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
