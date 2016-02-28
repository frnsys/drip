import unittest
from drip.datastore import db
from drip.api import create_app

test_config = {
    'SQLALCHEMY_DATABASE_URI': 'postgresql://drip_user:password@localhost:5432/drip_test'
}


class TestCase(unittest.TestCase):
    def __call__(self, result=None):
        """
        Sets up the tests without needing
        to call setUp.
        """
        try:
            self._pre_setup()
            super().__call__(result)
        finally:
            self._post_teardown()

    def _pre_setup(self):
        self.app = create_app(**test_config)
        self.client = self.app.test_client()

        self._ctx = self.app.test_request_context()
        self._ctx.push()

        self.db = db

        with self.app.app_context():
            self.db.create_all()

    def _post_teardown(self):
        if self._ctx is not None:
            self._ctx.pop()

        with self.app.app_context():
            self.db.session.remove()
            self.db.drop_all()

        del self.app
        del self.client
        del self._ctx
