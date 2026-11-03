import csv
import io
import os
import sys
from typing import Any, Tuple

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

import json
import logging
from collections import defaultdict
from io import StringIO

import pandas as pd
from database.models import tollpasses, tollstations
from flask import Blueprint, Response, jsonify, request
from login.loginsystem import role_required

admin_bp = Blueprint("admin", __name__)

VALID_COLUMNS_TOLLSTATIONS = [
    "OpID",
    "Operator",
    "TollID",
    "Name",
    "PM",
    "Locality",
    "Road",
    "Lat",
    "Long",
    "Email",
    "Price1",
    "Price2",
    "Price3",
    "Price4",
]

VALID_COLUMNS_TOLLPASSES = [
    "timestamp",
    "tollID",
    "tagRef",
    "tagHomeID",
    "charge",
]


@admin_bp.route("/api/admin/healthcheck", methods=["GET"])  # type: ignore
@role_required("Admin")  # type: ignore
def healthcheck() -> Tuple[Any, int]:
    """
    Performs a healthcheck with the mongodb database
    Returns the status of the connection with the database,
    the total unique number of tollstations, tags and passes
    :method: GET
    """
    try:
        tollstations_list = [station.to_json() for station in tollstations.objects()]
        pass_list = [pass_obj.to_json() for pass_obj in tollpasses.objects()]

        n_stations = defaultdict(int)  # type: ignore
        n_tags = defaultdict(int)  # type: ignore
        n_passes = len(pass_list)  # We just need the length of the pass list

        for row in tollstations_list:  # Compute how many unique TollID's we have
            n_stations[row["TollID"]] += 1

        for row in pass_list:  # Compute how many unique Tags we have
            n_tags[row["tagRef"]] += 1

        returned_json = {
            "status": "OK",
            "dbconnection": "Connected",
            "n_stations": int(len(n_stations)),
            "n_tags": int(len(n_tags)),
            "n_passes": int(n_passes),
        }

        response_format = request.args.get("format", "json").lower()

        if response_format == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(returned_json.keys())
            writer.writerow(returned_json.values())

            response = Response(output.getvalue(), mimetype="text/csv")
            response.headers["Content-Disposition"] = (
                "attachment; filename=healthcheck.csv"
            )
            return response, 200
        else:
            return jsonify(returned_json), 200
    except Exception as e:
        return (
            jsonify(
                {
                    "status": "failed",
                    "dbconnection": f"Failed - {str(e)}",
                }
            ),
            500,
        )


@admin_bp.route("/api/admin/getstations", methods=["GET"])  # type: ignore
@role_required("Admin")  # type: ignore
def getstations() -> Tuple[Any, int]:
    """
    - Returns a json with all the tollstations information
    """
    try:
        tollstations_list = [station.to_json() for station in tollstations.objects()]
        returned_json = {
            "total_stations": len(tollstations_list),
            "stations": tollstations_list,
        }

        response_format = request.args.get("format", "json").lower()

        if response_format == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(returned_json.keys())
            writer.writerow(returned_json.values())

            response = Response(output.getvalue(), mimetype="text/csv")
            response.headers["Content-Disposition"] = (
                "attachment; filename=get_stations.csv"
            )
            return response, 200
        else:
            return jsonify(returned_json), 200
    except Exception as e:
        logging.error(f"Error processing tollstations: {e}")
        return jsonify({"status": "failed", "info": "Internal server error"}), 500


@admin_bp.route("/api/admin/resetstations", methods=["POST"])  # type: ignore
@role_required("Admin")  # type: ignore
def resetstations() -> Tuple[Any, int]:
    """
    - Delete every object from tollstations
    - Fills the tollstations object with the new data
    :method: POST

    :rtype: Tuple[Any, int]
    """
    tollstations.objects().delete()
    data = request.data.decode("utf-8")
    extra = request.args.to_dict(flat=False)

    if extra and extra["format"] == ["csv"]:
        try:
            toll_stations_df = pd.read_csv(StringIO(data), skipinitialspace=True)
            passed_data_cols = list(toll_stations_df.columns)

            if len(passed_data_cols) != len(VALID_COLUMNS_TOLLSTATIONS):
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
                if col not in VALID_COLUMNS_TOLLSTATIONS:
                    return (
                        jsonify(
                            {
                                "status": "failed",
                                "info": "Passed data columns are not correct",
                            }
                        ),
                        400,
                    )

            for _, row in toll_stations_df.iterrows():
                toll_station = tollstations(**row.to_dict())
                toll_station.save()

            return jsonify({"status": "OK"}), 200
        except Exception as e:
            logging.error(f"Error processing the CSV file: {e}")
            return jsonify({"status": "failed", "info": "Internal server error"}), 500
    else:
        try:
            json_data = json.loads(data)
            if isinstance(json_data, list):
                passed_data_cols = list(json_data[0].keys())
            elif isinstance(json_data, dict):
                passed_data_cols = list(json_data.keys())
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

            if len(passed_data_cols) != len(VALID_COLUMNS_TOLLSTATIONS):
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
                if col not in VALID_COLUMNS_TOLLSTATIONS:
                    return (
                        jsonify(
                            {
                                "status": "failed",
                                "info": "Passed data columns are not correct",
                            }
                        ),
                        400,
                    )

            if isinstance(json_data, list):
                for entry in json_data:
                    new_row = tollstations(**entry)
                    new_row.save()
            elif isinstance(json_data, dict):
                new_row = tollstations(**json_data)
                new_row.save()

            return jsonify({"status": "OK"}), 200
        except Exception as e:
            logging.error(f"Error processing the json file {e}")
            return jsonify({"status": "failed", "info": "Internal server error"}), 500


@admin_bp.route("/api/admin/addpasses", methods=["POST"])  # type: ignore
@role_required("Admin")  # type: ignore
def addpasses() -> Tuple[Any, int]:
    """
    - Add the passed passes in the database
    """
    data = request.data.decode("utf-8")
    extra = request.args.to_dict(flat=False)

    if extra and extra["format"] == ["csv"]:
        try:
            toll_passes_df = pd.read_csv(StringIO(data), skipinitialspace=True)
            passed_data_cols = list(toll_passes_df.columns)

            if len(passed_data_cols) != len(VALID_COLUMNS_TOLLPASSES):
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
                if col not in VALID_COLUMNS_TOLLPASSES:
                    return (
                        jsonify(
                            {
                                "status": "failed",
                                "info": "Passed data columns are not correct",
                            }
                        ),
                        400,
                    )

            for _, row in toll_passes_df.iterrows():
                toll_pass = tollpasses(**row.to_dict())
                toll_pass.save()

            return jsonify({"status": "OK"}), 200
        except Exception as e:
            logging.error(f"Error processing the CSV file: {e}")
            return jsonify({"status": "failed", "info": "Internal server error"}), 500
    else:
        try:
            json_data = json.loads(data)
            if isinstance(json_data, list):
                passed_data_cols = list(json_data[0].keys())
            elif isinstance(json_data, dict):
                passed_data_cols = list(json_data.keys())
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

            if len(passed_data_cols) != len(VALID_COLUMNS_TOLLPASSES):
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
                if col not in VALID_COLUMNS_TOLLPASSES:
                    return (
                        jsonify(
                            {
                                "status": "failed",
                                "info": "Passed data columns are not correct",
                            }
                        ),
                        400,
                    )

            if isinstance(json_data, list):
                for entry in json_data:
                    new_row = tollpasses(**entry)
                    new_row.save()
            elif isinstance(json_data, dict):
                new_row = tollpasses(**json_data)
                new_row.save()

            return jsonify({"status": "OK"}), 200
        except Exception as e:
            logging.error(f"Error processing the json file {e}")
            return jsonify({"status": "failed", "info": "Internal server error"}), 500


@admin_bp.route("/api/admin/resetpasses", methods=["POST"])  # type: ignore
@role_required("Admin")  # type: ignore
def resetpasses() -> Tuple[Any, int]:
    """
    - Delete every object from passes
    - Fills the passes object with the new data
    """
    try:
        tollpasses.objects().delete()
        return jsonify({"status": "OK"}), 200
    except Exception as e:
        logging.error(f"Error reseting the passes: {e}")
        return jsonify({"status": "failed", "info": e}), 500
