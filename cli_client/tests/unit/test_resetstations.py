import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../back-end"))
)

import unittest

from apis.REST.app import create_app
from database.db import db
from database.models import Session, tollstations


class TestResetStations(unittest.TestCase):
    """
    Class that contains test cases for the /resetstations
    api call
    """

    def setUp(self) -> None:
        self.db = db
        self.app = create_app().test_client()
        Session.objects().delete()
        tollstations.objects().delete()

    def tearDown(self) -> None:
        Session.objects().delete()
        tollstations.objects().delete()

    def test_resetstations(self) -> None:
        os.system("se2404 login --username admin --password freepasses4all")
        os.system("se2404 resetstations")

        self.assertEqual(len(tollstations.objects()), 253)
