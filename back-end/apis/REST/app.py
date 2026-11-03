import os
import sys
import threading
import time
from typing import Any

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))


import requests  # type: ignore
from database.db import initialize_db
from database.models import User
from flask import Flask, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
from werkzeug.security import generate_password_hash

from scheduler.scheduler import run_scheduler

from .admin.admin import admin_bp
from .login.loginsystem import user_bp
from .tollstations.charges_by import chargesby_bp
from .tollstations.get_passes import getpasses_bp
from .tollstations.pass_analysis import passanalysis_bp
from .tollstations.passes_cost import passescost_bp
from .tollstations.tollstation_passes import tollstation_passes_bp

BASE_URL = "http://127.0.0.1:9115"
SWAGGER_URL = "/api/docs"
API_URL = "../../../documentation/swagger.json"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "TollSync: Interoperable Data Hub for Highway Networks"},
)


def create_app() -> Any:
    """
    Author: @spirosmaggioros
    Creates the flask app and returns it
    :returns: a Flask() App with the mongodb configuration
    :rtype: Flask app
    """
    app = Flask(__name__)

    app.config["MONGO_URI"] = "mongodb://localhost:9115/softeng24-04"
    app.config["MAX_CONTENT_LENGTH"] = (
        128 * 1024 * 1024
    )  # Accept up to 128 MB files, we may need to change this later

    # Initialize mongodb connection
    initialize_db(app)

    # Register blueprints for tollstations and admins
    app.register_blueprint(admin_bp)
    app.register_blueprint(passanalysis_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(tollstation_passes_bp)
    app.register_blueprint(passescost_bp)
    app.register_blueprint(chargesby_bp)
    app.register_blueprint(getpasses_bp)

    # Swagger documentation
    app.register_blueprint(swaggerui_blueprint)

    @app.route("/documentation/swagger.json")  # type: ignore
    def send_swagger() -> Any:
        return send_from_directory("documentation", "swagger.json")

    return app


def perform_startup_post_request() -> None:
    """
    Perform a POST request after the server has started.
    """
    time.sleep(5)  # Wait for the server to start
    try:
        password = generate_password_hash("freepasses4all")
        init_admin_acc = User(
            username="admin",
            password=password,
            role="Admin",
        )
        init_admin_acc.save()

        password = generate_password_hash("notfreepasses4all")
        init_user_acc = User(
            username="user",
            password=password,
            role="Employee",
        )
        init_user_acc.save()
    except requests.exceptions.RequestException as e:
        print(f"Failed to perform startup POST request: {e}")


def start_reporting() -> None:
    time.sleep(5)
    run_scheduler()


if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Thread(target=perform_startup_post_request).start()
        threading.Thread(target=start_reporting).start()
    _app = create_app()
    _app.run(debug=True, port=9115)
