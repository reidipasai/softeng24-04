import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../back-end"))
)

import unittest

from apis.REST.app import create_app
from database.db import db
from database.models import Session


class TestUserLogin(unittest.TestCase):
    """
    Class that contains test cases for the /login
    api call
    """

    def setUp(self) -> None:
        self.db = db
        self.app = create_app().test_client()
        Session.objects().delete()

    def tearDown(self) -> None:
        Session.objects().delete()

    def test_user_login(self) -> None:
        os.system("se2404 login --username admin --password freepasses4all")

        token_in_db = Session.objects(username="admin").first()

        self.assertEqual(token_in_db.username, "admin")
        os.system("se2404 logout")

    def test_invalid_username(self) -> None:
        os.system("se2404 login --username wronguser --password adminpassword1")
        self.assertTrue(len(Session.objects(username="wronguser")) == 0)

    def test_invalid_password(self) -> None:
        os.system("se2404 login --username admin --password wrongpassword")

        self.assertTrue(len(Session.objects(username="admin")) == 0)
