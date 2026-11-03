from typing import Any

from flask_mongoengine import MongoEngine

db = MongoEngine()


def initialize_db(app: Any) -> None:
    db.init_app(app)
