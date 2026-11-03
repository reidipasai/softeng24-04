import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../back-end"))
)

import unittest

from apis.REST.app import create_app
from database.db import db
from database.models import Session


class TestUserLogout(unittest.TestCase):
    """
    Contains test cases for the /logout api call
    """

    def setUp(self) -> None:
        self.db = db
        self.app = create_app().test_client()
        Session.objects().delete()

    def tearDown(self) -> None:
        Session.objects().delete()

    def test_user_logout(self) -> None:

        os.system("se2404 login --username admin --password freepasses4all")

        self.assertTrue(len(Session.objects()) > 0)
        token = Session.objects(username="admin").first()

        os.system("se2404 logout")
        # # # TODO: Here we just check if it exists in the session database, as you know
        # # # if you logout, the token is removed from the db. So, we need more like-this
        # # # type of unit tests.
        session_in_db = Session.objects(token=token["token"]).first()
        self.assertIsNone(session_in_db)
