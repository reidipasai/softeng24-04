import argparse
import json
import os
import sys
from io import BytesIO
from typing import Any

import requests  # type: ignore

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../back-end")))

from database.models import Session
from mongoengine import connect

from .tollstations2024 import tollstations_df

connect("test", host="mongodb://localhost:27017/test")

VERSION = "0.0.1"
BASE_URL = "http://127.0.0.1:9115"


def get_session_file() -> Any:
    if os.name == "nt":
        config_dir = os.path.join(os.getenv("APPDATA"), "se2404")  # type: ignore
    else:
        config_dir = os.path.join(os.path.expanduser("~"), ".config", "se2404")

    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, "session.json")


SESSION_FILE = get_session_file()

session_usr = None


def save_session() -> None:
    session_data = {"username": session_usr}
    with open(SESSION_FILE, "w") as f:
        json.dump(session_data, f)


def load_session() -> None:
    global session_usr, session_psd, session_tkn
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            session_data = json.load(f)
            session_usr = session_data.get("username")


def clear_session() -> None:
    global session_usr, session_psd, session_tkn
    session_usr = None
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)


def run_register(args: Any) -> None:
    load_session()
    global session_usr

    session = Session.objects(username=session_usr).first()
    if session_usr is not None and session is None:
        print(
            "It look like the token is missing. Did you log out?\n Clearing the session...\nYou can try again now"
        )
        clear_session()
        return

    assert args.username is not None, "Username is missing"
    assert args.password is not None, "Password is missing"
    assert args.role is not None, "Role is missing"

    response = requests.post(
        f"{BASE_URL}/api/register",
        json={"username": args.username, "password": args.password, "role": args.role},
        headers={"X-OBSERVATORY-AUTH": session["token"]},
    )
    assert response.status_code == 200, f"{response.json()}"
    print(response.json())


def run_login(args: Any) -> None:
    load_session()
    global session_usr

    assert args.username is not None, "Username is missing"
    assert args.password is not None, "Password is missing"

    session = Session.objects(username=session_usr).first()
    if session_usr is not None and session is None:
        print(
            "It look like the token is missing. Did you log out?\n Clearing the session...\nYou can try again now"
        )
        clear_session()
        return

    session = Session.objects(username=args.username).first()
    if session is not None:
        session_usr = args.username
        print("Successfully logged in")
    else:
        response = requests.post(
            f"{BASE_URL}/api/login",
            json={"username": args.username, "password": args.password},
        )
        assert response.status_code == 200, f"{response.json()}"

        session_usr = args.username
        print("Successfully logged in")

    save_session()


def run_logout(args: Any) -> None:
    load_session()
    global session_usr

    session = Session.objects(username=session_usr).first()
    if session_usr is not None and session is None:
        print(
            "It look like the token is missing. Did you log out?\n Clearing the session...\nYou can try again now"
        )
        clear_session()
        return

    assert session is not None, "User is not logged in"

    response = requests.post(
        f"{BASE_URL}/api/logout",
        headers={"X-OBSERVATORY-AUTH": session["token"]},
    )

    assert response.status_code == 204, f"{response.json()}"
    print(f"User {session_usr} logged out")
    session_usr = None

    save_session()


def run_healthcheck(args: Any) -> None:
    load_session()
    global session_usr

    session = Session.objects(username=session_usr).first()
    if session_usr is not None and session is None:
        print(
            "It look like the token is missing. Did you log out?\n Clearing the session...\nYou can try again now"
        )
        clear_session()
        return

    response = requests.get(
        f"{BASE_URL}/api/admin/healthcheck",
        headers={"X-OBSERVATORY-AUTH": session["token"]},
    )
    assert response.status_code == 200, f"{response.json()}"
    print(response.json())

    save_session()


def run_getstations(args: Any) -> None:
    load_session()
    global session_usr

    assert args.format in ["json", "csv"], f"Invalid format: {args.format}"

    session = Session.objects(username=session_usr).first()
    if session_usr is not None and session is None:
        print(
            "It look like the token is missing. Did you log out?\n Clearing the session...\nYou can try again now"
        )
        clear_session()
        return

    response = requests.get(
        f"{BASE_URL}/api/admin/getstations?format={args.format}",
        headers={"X-OBSERVATORY-AUTH": session["token"]},
    )
    assert response.status_code == 200, f"{response.json()}"

    if args.format == "json":
        print(response.json())
    elif args.format == "csv":
        output_filename = "get_stations.csv"
        with open(output_filename, "wb") as f:
            f.write(response.content)

        print(f"CSV file saved as: {output_filename}")

    save_session()


def run_resetstations(args: Any) -> None:
    load_session()
    global session_usr

    session = Session.objects(username=session_usr).first()
    if session_usr is not None and session is None:
        print(
            "It look like the token is missing. Did you log out?\n Clearing the session...\nYou can try again now"
        )
        clear_session()
        return

    response = requests.post(
        f"{BASE_URL}/api/admin/resetstations?format=csv",
        data=BytesIO(tollstations_df.encode("utf-8")),
        headers={"Content-Type": "text/csv", "X-OBSERVATORY-AUTH": session["token"]},
    )
    assert response.status_code == 200, f"{response.json()}"

    print(response.json())

    save_session()


def run_resetpasses(args: Any) -> None:
    load_session()
    global session_usr

    session = Session.objects(username=session_usr).first()
    if session_usr is not None and session is None:
        print(
            "It look like the token is missing. Did you log out?\n Clearing the session...\nYou can try again now"
        )
        clear_session()
        return

    response = requests.post(
        f"{BASE_URL}/api/admin/resetpasses",
        headers={"X-OBSERVATORY-AUTH": session["token"]},
    )
    assert response.status_code == 200, f"{response.json()}"

    print(response.json())

    save_session()


def run_chargesby(args: Any) -> None:
    load_session()
    global session_usr

    assert args.op is not None, "Operator ID is missing"
    assert args.datefrom is not None, "Date from is missing"
    assert args.dateto is not None, "Date to is missing"
    assert args.format in ["json", "csv"], f"Invalid format: {args.format}"

    session = Session.objects(username=session_usr).first()
    if session_usr is not None and session is None:
        print(
            "It look like the token is missing. Did you log out?\n Clearing the session...\nYou can try again now"
        )
        clear_session()
        return

    response = requests.get(
        f"{BASE_URL}/api/chargesBy/{args.op}/{args.datefrom}/{args.dateto}?format={args.format}"
    )
    assert response.status_code == 200, f"{response.json()}"

    if args.format == "json":
        print(response.json())
    elif args.format == "csv":
        output_filename = "charges_by.csv"
        with open(output_filename, "wb") as f:
            f.write(response.content)

        print(f"CSV file saved as: {output_filename}")

    save_session()


def run_passanalysis(args: Any) -> None:
    load_session()
    global session_usr

    assert args.stationop is not None, "Station operator ID is missing"
    assert args.tagop is not None, "Tag operator ID is missing"
    assert args.datefrom is not None, "Date from is missing"
    assert args.dateto is not None, "Date to is missing"
    assert args.format in ["json", "csv"], f"Invalid format: {args.format}"

    session = Session.objects(username=session_usr).first()
    if session_usr is not None and session is None:
        print(
            "It look like the token is missing. Did you log out?\n Clearing the session...\nYou can try again now"
        )
        clear_session()
        return

    response = requests.get(
        f"{BASE_URL}/api/passAnalysis/{args.stationop}/{args.tagop}/{args.datefrom}/{args.dateto}?format={args.format}"
    )
    assert response.status_code == 200, f"{response.json()}"

    if args.format == "json":
        print(response.json())
    elif args.format == "csv":
        output_filename = "pass_analysis.csv"
        with open(output_filename, "wb") as f:
            f.write(response.content)

        print(f"CSV file saved as: {output_filename}")

    save_session()


def run_passescost(args: Any) -> None:
    load_session()
    global session_usr

    assert args.tollop is not None, "Toll operator ID is missing"
    assert args.tagop is not None, "Tag operator ID is missing"
    assert args.datefrom is not None, "Date from is missing"
    assert args.dateto is not None, "Date to is missing"
    assert args.format in ["json", "csv"], f"Invalid format: {args.format}"

    session = Session.objects(username=session_usr).first()
    if session_usr is not None and session is None:
        print(
            "It look like the token is missing. Did you log out?\n Clearing the session...\nYou can try again now"
        )
        clear_session()
        return

    response = requests.get(
        f"{BASE_URL}/api/passesCost/{args.tollop}/{args.tagop}/{args.datefrom}/{args.dateto}?format={args.format}"
    )
    assert response.status_code == 200, f"{response.json()}"

    if args.format == "json":
        print(response.json())
    elif args.format == "csv":
        output_filename = "passes_cost.csv"
        with open(output_filename, "wb") as f:
            f.write(response.content)

        print(f"CSV file saved as: {output_filename}")

    save_session()


def run_tollstationpasses(args: Any) -> None:
    load_session()
    global session_usr

    assert args.station is not None, "Station ID is missing"
    assert args.datefrom is not None, "Date from is missing"
    assert args.dateto is not None, "Date to is missing"
    assert args.format in ["json", "csv"], f"Invalid format: {args.format}"

    session = Session.objects(username=session_usr).first()
    if session_usr is not None and session is None:
        print(
            "It look like the token is missing. Did you log out?\n Clearing the session...\nYou can try again now"
        )
        clear_session()
        return

    response = requests.get(
        f"{BASE_URL}/api/tollStationPasses/{args.station}/{args.datefrom}/{args.dateto}?format={args.format}"
    )
    assert response.status_code == 200, f"{response.json()}"

    if args.format == "json":
        print(response.json())
    elif args.format == "csv":
        output_filename = "tollstation_passes.csv"
        with open(output_filename, "wb") as f:
            f.write(response.content)

        print(f"CSV file saved as: {output_filename}")

    save_session()


def run_admin(args: Any) -> None:
    load_session()
    global session_usr

    assert args.addpasses is not None
    assert args.source is not None, "Didn't provide any souce file"

    session = Session.objects(username=session_usr).first()
    if session_usr is not None and session is None:
        print(
            "It look like the token is missing. Did you log out?\n Clearing the session...\nYou can try again now"
        )
        clear_session()
        return

    ext = os.path.splitext(args.source)[1].lower()
    assert ext in {".json", ".csv"}, "Wrong file suffix"
    assert os.path.isfile(args.source), "File doesn't exist"

    if ext == ".json":
        with open(args.source, "r", encoding="utf-8") as f:
            data = json.load(f)
        response = requests.post(
            f"{BASE_URL}/api/admin/addpasses",
            json=data,
            headers={"X-OBSERVATORY-AUTH": session["token"]},
        )
        assert response.status_code == 200, f"{response.json()}"
    else:
        with open(args.source, "r", encoding="utf-8-sig") as f:
            csv_content = f.read()
        response = requests.post(
            f"{BASE_URL}/api/admin/addpasses?format=csv",
            data=csv_content.encode("utf-8"),
            headers={
                "Content-Type": "text/csv",
                "X-OBSERVATORY-AUTH": session["token"],
            },
        )
        assert response.status_code == 200, f"{response.json()}"

    print(response.json())
    save_session()


def run_info(args: Any) -> None:
    load_session()
    global session_usr

    session = Session.objects(username=session_usr).first()
    if session_usr is not None and session is None:
        print(
            "It look like the token is missing. Did you log out?\n Clearing the session...\nYou can try again now"
        )
        clear_session()
        return

    returned = {
        "username": session_usr,
    }
    if session_usr is None:
        print("{No sessions found}")
    else:
        returned = {"username": session_usr, "token": session["token"]}
        print(returned)


def main() -> None:
    global session_usr, session_psd, session_tkn
    prog = "se2404"
    description = "CLI interface for the TollSync application"

    usage = f"""
        se2404 v{VERSION}
        register:
            Registers a new user.
            Parameters:
                --username: The username
                --password: The password
                --role: The role of the user[Admin, Employee]
            (se2404 register --username [username] --password [passcode] --role [role])
        login:
            Logins with the passed username and password.
            Parameters:
                --username: The username
                --password: The password
            (se2404 login --username [username] --password [password])
        logout:
            Logouts the currently connected user
            (se2404 logout)
        healthcheck:
            Perform healthcheck with the database [ADMIN PRIVILEGES NEEDED].
            (se2404 healthcheck)
        getstations:
            Returns a json or csv file with all the tollstations information [ADMIN PRIVILEGES NEEDED].
            Parameters:
                --format: json or csv (default is csv)
            (se2404 getstations --format [format])
        resetstations:
            Deletes every object from tollstations and fills the tollstations object with the new data [ADMIN PRIVILEGES NEEDED].
            (se2404 resetstations)
        chargesby:
            Returns a json or csv file with data about the passes that happened from users with different.
            Parameters:
                --op: Operator ID
                --from: Date from
                --to: Date to
                --format: json or csv (default is csv)
            (se2404 chargesby --opid [op] --from [datefrom] --to [dateto] --format [format])
        passanalysis:
            Returns a json or csv file with data about the total passes.
            Parameters:
                --stationop: Station operator ID
                --tagop: Tag operator ID
                --from: Date from
                --to: Date to
                --format: json or csv (default is csv)
            (se2404 passanalysis --stationop [stationop] --tagop [tagop] --from [datefrom] --to [dateto] --format [format])
        passescost:
            Returns a json or csv file with data about the passes that happened from users with tagOpID on the stations with tollOpID.
            Parameters:
                --stationop: Toll operator ID
                --tagop: Tag operator ID
                --from: Date from
                --to: Date to
                --format: json or csv (default is csv)
            (se2404 passescost --stationop [tollop] --tagop [tagop] --from [datefrom] --to [dateto] --format [format])
        resetpasses:
            Resets(clears) the passes in the database [ADMIN PRIVILEGES NEEDED]
        (se2404 resetpasses)
        admin:
            Can only perform addpasses as of now.
            Parameters:
                --addpasses(boolean)
                --source [filename]
            (se2404 --addpasses --source [filename])
        tollstationpasses:
            Returns a json or csv file with data about the tollstation passes of the passed tollstation ID from date_from to date_to.
            Parameters:
                --station: Station ID
                --from: Date from
                --to: Date to
                --format: json or csv (default is csv)
            (se2404 tollstationpasses --station [station] --from [datefrom] --to [dateto] --format [format])
        info:
            Returns the username and the token of the connected user
            (se2404 info)

    """
    parser = argparse.ArgumentParser(
        prog=prog, usage=usage, description=description, add_help=False
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # register
    register = subparsers.add_parser(
        "register",
        help="Registers a user with providing [username, password, role]. [ADMIN PRIVILEGE NEEDED]",
    )
    register.add_argument(
        "--username",
        type=str,
        dest="username",
        required=True,
    )
    register.add_argument(
        "--password",
        type=str,
        dest="password",
        required=True,
    )
    register.add_argument(
        "--role",
        type=str,
        dest="role",
        required=True,
    )
    register.set_defaults(func=run_register)

    # login
    login = subparsers.add_parser(
        "login", help="Performs login to the TOMS application"
    )
    login.add_argument(
        "--username",
        type=str,
        dest="username",
        required=True,
    )
    login.add_argument(
        "--password",
        type=str,
        dest="password",
        required=True,
    )
    login.set_defaults(func=run_login)

    # logout
    logout = subparsers.add_parser(
        "logout", help="Performs logout of the TOMS application"
    )
    logout.set_defaults(func=run_logout)

    # healthcheck
    healthcheck = subparsers.add_parser(
        "healthcheck",
        help="Perform healthcheck with the database [ADMIN PRIVILEGES NEEDED]",
    )
    healthcheck.set_defaults(func=run_healthcheck)

    # getstations
    getstations = subparsers.add_parser(
        "getstations",
        help="Returns a json with all the tollstations information [ADMIN PRIVILEGES NEEDED]",
    )
    getstations.add_argument(
        "--format",
        type=str,
        dest="format",
        choices=["json", "csv"],
        default="csv",
    )
    getstations.set_defaults(func=run_getstations)

    # resetstations
    resetstations = subparsers.add_parser(
        "resetstations",
        help="Deletes every object from tollstations and fills the tollstations object with the new data [ADMIN PRIVILEGES NEEDED]",
    )
    resetstations.set_defaults(func=run_resetstations)

    # chargesby
    chargesby = subparsers.add_parser(
        "chargesby",
        help="Returns a json or csv file with data about the passes that happened from users with different",
    )
    chargesby.add_argument(
        "--opid",
        type=str,
        dest="op",
        required=True,
    )
    chargesby.add_argument(
        "--from",
        type=str,
        dest="datefrom",
        required=True,
    )
    chargesby.add_argument(
        "--to",
        type=str,
        dest="dateto",
        required=True,
    )
    chargesby.add_argument(
        "--format",
        type=str,
        dest="format",
        choices=["json", "csv"],
        default="csv",
    )
    chargesby.set_defaults(func=run_chargesby)

    # passanalysis
    passanalysis = subparsers.add_parser(
        "passanalysis",
        help="Retrieve pass analysis data for a station and tag operator",
    )
    passanalysis.add_argument(
        "--stationop",
        type=str,
        dest="stationop",
        required=True,
    )
    passanalysis.add_argument(
        "--tagop",
        type=str,
        dest="tagop",
        required=True,
    )
    passanalysis.add_argument(
        "--from",
        type=str,
        dest="datefrom",
        required=True,
    )
    passanalysis.add_argument(
        "--to",
        type=str,
        dest="dateto",
        required=True,
    )
    passanalysis.add_argument(
        "--format",
        type=str,
        dest="format",
        choices=["json", "csv"],
        default="csv",
    )
    passanalysis.set_defaults(func=run_passanalysis)

    # passescost
    passescost = subparsers.add_parser(
        "passescost",
        help="Returns a json or csv with data about the passes that happened from users with tagOpID on the stations with tollOpID.",
    )
    passescost.add_argument(
        "--stationop",
        type=str,
        dest="tollop",
        required=True,
    )
    passescost.add_argument(
        "--tagop",
        type=str,
        dest="tagop",
        required=True,
    )
    passescost.add_argument(
        "--from",
        type=str,
        dest="datefrom",
        required=True,
    )
    passescost.add_argument(
        "--to",
        type=str,
        dest="dateto",
        required=True,
    )
    passescost.add_argument(
        "--format",
        type=str,
        dest="format",
        choices=["json", "csv"],
        default="csv",
    )
    passescost.set_defaults(func=run_passescost)

    # tollstationpasses
    tollstationpasses = subparsers.add_parser(
        "tollstationpasses",
        help="Returns a json or csv with data about the tollstation passes of the passed tollstation ID from date_from to date_to",
    )
    tollstationpasses.add_argument(
        "--station",
        type=str,
        dest="station",
        required=True,
    )
    tollstationpasses.add_argument(
        "--from",
        type=str,
        dest="datefrom",
        required=True,
    )
    tollstationpasses.add_argument(
        "--to",
        type=str,
        dest="dateto",
        required=True,
    )
    tollstationpasses.add_argument(
        "--format",
        type=str,
        dest="format",
        choices=["json", "csv"],
        default="csv",
    )
    tollstationpasses.set_defaults(func=run_tollstationpasses)

    # resetpasses
    resetpasses = subparsers.add_parser(
        "resetpasses", help="Resets the passes in the database"
    )
    resetpasses.set_defaults(func=run_resetpasses)

    # admin
    admin = subparsers.add_parser("admin", help="Support for addpasses API call")
    admin.add_argument(
        "--addpasses",
        action="store_true",
        dest="addpasses",
    )
    admin.add_argument(
        "--source",
        type=str,
        dest="source",
    )
    admin.set_defaults(func=run_admin)

    # get info
    info = subparsers.add_parser(
        "info", help="Returns information about the connected user"
    )
    info.set_defaults(func=run_info)

    args = parser.parse_args()
    args.func(args)
