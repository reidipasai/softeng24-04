import json
import logging
import os
import sys
from functools import wraps
from io import StringIO
from typing import Any, Callable, Optional, Tuple

import pandas as pd
from database.models import Session, User
from flask import Blueprint, jsonify, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

user_bp = Blueprint("user", __name__)

VALID_COLUMNS_USERS = ["username", "password", "role"]

SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey")
serializer = URLSafeTimedSerializer(SECRET_KEY)


def role_required(required_role: str) -> Callable:
    """
    Wrapper function that requires an "Admin" role if called with role_required("Admin")

    :param required_role: The passed required role. Either "Admin" or "Employee"
    :type required_role: str
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            token = request.headers.get("X-OBSERVATORY-AUTH")
            if not token:
                return jsonify({"status": "failed", "info": "Token missing"}), 400

            try:
                username = serializer.loads(token)
            except (BadSignature, SignatureExpired):
                return (
                    jsonify({"status": "failed", "info": "Invalid or expired token"}),
                    400,
                )

            user = User.objects(username=username).first()
            if not user:
                return jsonify({"status": "failed", "info": "User not found"}), 400

            if user.role != required_role:
                return jsonify({"status": "failed", "info": "Access denied"}), 401

            return func(*args, **kwargs)

        return wrapper

    return decorator


@user_bp.route("/api/register", methods=["POST"])  # type: ignore
@role_required("Admin")
def register() -> Tuple[Any, int]:
    """
    Register new users. Accepts CSV or JSON data with support for multiple users.
    :method: POST
    """
    data = request.data.decode("utf-8")
    extra = request.args.to_dict(flat=False)

    if extra and extra["format"] == ["csv"]:
        try:
            users_df = pd.read_csv(StringIO(data), skipinitialspace=True)
            passed_data_cols = list(users_df.columns)

            if len(passed_data_cols) != len(VALID_COLUMNS_USERS):
                return (
                    jsonify(
                        {
                            "status": "failed",
                            "info": "Passed data columns are not correct",
                        }
                    ),
                    400,
                )

            for col in passed_data_cols:
                if col not in VALID_COLUMNS_USERS:
                    return (
                        jsonify(
                            {
                                "status": "failed",
                                "info": "Passed data columns are not correct",
                            }
                        ),
                        400,
                    )

            for _, row in users_df.iterrows():
                hashed_password = generate_password_hash(row["password"])
                user = User(
                    username=row["username"], password=hashed_password, role=row["role"]
                )
                user.save()

            return jsonify({"status": "OK"}), 200
        except Exception as e:
            logging.error(f"Error processing CSV: {e}")
            return jsonify({"status": "failed", "info": "Internal server error"}), 500

    else:
        try:
            json_data = json.loads(data)
            if isinstance(json_data, list):
                for entry in json_data:
                    passed_data_cols = list(entry.keys())

                    if len(passed_data_cols) != len(VALID_COLUMNS_USERS):
                        return (
                            jsonify(
                                {
                                    "status": "failed",
                                    "info": "Passed data columns are not correct",
                                }
                            ),
                            400,
                        )

                    for col in passed_data_cols:
                        if col not in VALID_COLUMNS_USERS:
                            return (
                                jsonify(
                                    {
                                        "status": "failed",
                                        "info": "Passed data columns are not correct",
                                    }
                                ),
                                400,
                            )

                    if entry["role"] not in ["Admin", "Stakeholder", "Employee"]:
                        return (
                            jsonify(
                                {
                                    "status": "failed",
                                    "info": "Passed data columns are not correct",
                                }
                            ),
                            400,
                        )

                    hashed_password = generate_password_hash(entry["password"])
                    user = User(
                        username=entry["username"],
                        password=hashed_password,
                        role=entry["role"],
                    )
                    user.save()

            elif isinstance(json_data, dict):
                passed_data_cols = list(json_data.keys())

                if len(passed_data_cols) != len(VALID_COLUMNS_USERS):
                    return (
                        jsonify(
                            {
                                "status": "failed",
                                "info": "Passed data columns are not correct",
                            }
                        ),
                        400,
                    )

                for col in passed_data_cols:
                    if col not in VALID_COLUMNS_USERS:
                        return (
                            jsonify(
                                {
                                    "status": "failed",
                                    "info": "Passed data columns are not correct",
                                }
                            ),
                            400,
                        )

                if json_data["role"] not in ["Admin", "Stakeholder", "Employee"]:
                    return (
                        jsonify(
                            {
                                "status": "failed",
                                "info": "Passed data columns are not correct",
                            }
                        ),
                        400,
                    )

                hashed_password = generate_password_hash(json_data["password"])
                user = User(
                    username=json_data["username"],
                    password=hashed_password,
                    role=json_data["role"],
                )
                user.save()

            else:
                return (
                    jsonify(
                        {
                            "status": "failed",
                            "info": "Passed data columns are not correct",
                        }
                    ),
                    400,
                )

            return jsonify({"status": "OK"}), 200
        except Exception as e:
            logging.error(f"Error processing JSON: {e}")
            return jsonify({"status": "failed", "info": "Internal server error"}), 500


@user_bp.route("/api/login", methods=["POST"])  # type: ignore
def login() -> Tuple[Any, int]:
    """
    Login a user. Accepts JSON or CSV data with username and password.
    :method: POST
    """
    data = request.data.decode("utf-8")
    extra = request.args.to_dict(flat=False)

    username: Optional[str] = None
    password: Optional[str] = None

    if extra.get("format") == ["csv"]:
        try:
            users_df = pd.read_csv(StringIO(data), skipinitialspace=True)
            passed_data_cols = list(users_df.columns)

            if len(passed_data_cols) != 2:
                return (
                    jsonify(
                        {
                            "status": "failed",
                            "info": "Passed data columns are not correct",
                        }
                    ),
                    400,
                )

            if "username" not in users_df.columns or "password" not in users_df.columns:
                return (
                    jsonify(
                        {
                            "status": "failed",
                            "info": "Passed data columns are not correct",
                        }
                    ),
                    400,
                )

            row = users_df.iloc[0]
            username = row["username"]
            password = row["password"]

        except Exception as e:
            logging.error(f"Error processing CSV: {e}")
            return jsonify({"status": "failed", "info": "Internal server error"}), 500
    else:
        try:
            json_data = json.loads(data)
            if isinstance(json_data, dict):
                passed_data_cols = list(json_data.keys())
            else:
                return jsonify({"status": "failed", "info": "Invalid data format"}), 400

            if len(passed_data_cols) != 2:
                return (
                    jsonify(
                        {
                            "status": "failed",
                            "info": "Passed data columns are not correct",
                        }
                    ),
                    400,
                )

            if (
                not passed_data_cols[0] in VALID_COLUMNS_USERS
                or not passed_data_cols[1] in VALID_COLUMNS_USERS
            ):
                return (
                    jsonify(
                        {
                            "status": "failed",
                            "info": "Passed data columns are not correct",
                        }
                    ),
                    400,
                )

            username = json_data.get("username")
            password = json_data.get("password")

        except Exception as e:
            logging.error(f"Error processing JSON: {e}")
            return jsonify({"status": "failed", "info": "Internal server error"}), 500

    try:
        user = User.objects(username=username).first()
        if not user or not check_password_hash(user.password, password):
            return jsonify({"status": "failed", "info": "Invalid credentials"}), 401

        if Session.objects(username=username):
            return jsonify({"status": "failed", "info": "Already logged in"}), 401

        size = len(Session.objects())
        if size == 1:
            Session.objects().delete()

        token = str(serializer.dumps(username))

        entry = {"token": token, "username": username}
        new_row = Session(**entry)
        new_row.save()

        return jsonify({"token": str(token)}), 200

    except Exception as e:
        logging.error(f"Error during login: {e}")
        return jsonify({"status": "failed", "info": "Internal server error"}), 500


@user_bp.route("/api/logout", methods=["POST"])  # type: ignore
def logout() -> Tuple[Any, int]:
    """
    Logout a user by invalidating the token.
    :method: POST
    """
    token = str(request.headers.get("X-OBSERVATORY-AUTH"))
    if token == "None":
        return jsonify({"status": "failed", "info": "token missing"}), 400

    try:
        session = Session.objects(token=token)

        if not session:
            return (
                jsonify(
                    {"status": "failed", "info": "token invalid or already logged out"}
                ),
                401,
            )

        username = str(serializer.loads(token))
        entry = {"token": token, "username": username}

        Session.objects(**entry).delete()

        return {}, 204
    except Exception as e:
        logging.error(f"Error during logout: {e}")
        return jsonify({"status": "failed", "info": "Internal server error"}), 500
