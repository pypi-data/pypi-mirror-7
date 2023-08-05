import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'viceroy.tests.djangoapp.settings'

from django.test.runner import setup_databases

from viceroy.api import build_test_case
from viceroy.contrib.django import ViceroyDjangoTestCase
from .core import ViceroyScanner

root = os.path.abspath(os.path.dirname(__file__))
test_file = os.path.join(root, 'djangoapp', 'static', 'tests.js')


class DatabaseTestCase(ViceroyDjangoTestCase):
    @classmethod
    def setUpClass(cls):
        cls.old_config = setup_databases(0, False)
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        old_names, mirrors = cls.old_config
        for connection, old_name, destroy in old_names:
            if destroy:
                connection.creation.destroy_test_db(old_name, verbosity=0)


ViceroyDjangoTests = build_test_case(
    'ViceroyDjangoTests',
    test_file,
    ViceroyScanner,
    DatabaseTestCase,
)
