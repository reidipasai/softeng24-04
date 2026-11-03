from datetime import datetime
from typing import Any, Dict

import pandas as pd
import requests  # type: ignore
import streamlit as st
from diagrams import (
    create_leaderboards,
    passes_revenue_bubble_chart,
    passes_revenue_stacked_bar,
    passes_treemap,
    plot_wheel_diagram,
    revenue_treemap,
)
from operations import cluster_data

BASE_URL = "http://127.0.0.1:9115"

# Load the CSV data
tollstations_df = pd.read_csv("../shared/tollstations2024.csv")
date_from_global, date_to_global = None, None


def fetch_tollstations() -> None:
    response = requests.get(
        f"{BASE_URL}/api/admin/getstations",
        headers={"X-OBSERVATORY-AUTH": st.session_state.token},
    )

    if response.status_code != 200:
        st.warning("Failed to fetch stations. Please try again later.")
        return
    else:
        st.success("Successfully fetched toll stations!")

    st.session_state.stations_data = response.json()


def load_tollstation_passes(  # type: ignore
    tollStationID: str, date_from: str, date_to: str
) -> Any | Dict[Any, Any]:
    try:
        response = requests.get(
            f"{BASE_URL}/api/tollStationPasses/{tollStationID}/{date_from}/{date_to}"
        )
        if response.status_code != 200:
            return False
        if response.headers.get("Content-Type") == "application/json":
            return response.json()
    except Exception:
        return False


def load_tollstation_revenue(  # type: ignore
    tollStationID: str, date_from: str, date_to: str
) -> Any | Dict[Any, Any]:
    try:
        response = requests.get(
            f"{BASE_URL}/api/chargesBySpecific/{tollStationID}/{date_from}/{date_to}"
        )
        if response.status_code != 200:
            return False
        if response.headers.get("Content-Type") == "application/json":
            return response.json()
    except Exception:
        return False


def fetch_passes_cost(
    tollOpID: str, tagOpID: str, date_from: str, date_to: str
) -> Dict[Any, Any]:
    response = requests.get(
        f"{BASE_URL}/api/passesCost/{tollOpID}/{tagOpID}/{date_from}/{date_to}"
    )
    if response.status_code != 200:
        st.warning("Failed to fetch passes cost. Please try again later.")
        return {}
    if response.headers.get("Content-Type") == "application/json":
        return response.json()  # type: ignore

    return {}


def fetch_pass_analysis(
    stationOpID: str, tagOpID: str, date_from: str, date_to: str
) -> Dict[Any, Any]:
    response = requests.get(
        f"{BASE_URL}/api/passAnalysis/{stationOpID}/{tagOpID}/{date_from}/{date_to}"
    )
    if response.status_code != 200:
        st.warning("Failed to fetch pass analysis. Please try again later.")
        return {}
    if response.headers.get("Content-Type") == "application/json":
        return response.json()  # type: ignore
    return {}


def fetch_charges_by(tollOpID: str, date_from: str, date_to: str) -> Dict[Any, Any]:
    response = requests.get(
        f"{BASE_URL}/api/chargesBy/{tollOpID}/{date_from}/{date_to}"
    )
    if response.status_code != 200:
        st.warning("Failed to fetch charges by. Please try again later.")
        return {}
    if response.headers.get("Content-Type") == "application/json":
        return response.json()  # type: ignore
    return {}


def select_operators() -> pd.DataFrame:
    selected_operators = st.sidebar.multiselect(
        "Select Operators", tollstations_df["Operator"].unique()
    )
    if selected_operators:
        return tollstations_df[tollstations_df["Operator"].isin(selected_operators)]
    return tollstations_df


def select_roads(filtered_stations: pd.DataFrame) -> pd.DataFrame:
    selected_roads = st.sidebar.multiselect(
        "Select Roads", filtered_stations["Road"].unique()
    )
    if selected_roads:
        return filtered_stations[filtered_stations["Road"].isin(selected_roads)]
    return filtered_stations


def select_localities(filtered_stations: pd.DataFrame) -> pd.DataFrame:
    selected_localities = st.sidebar.multiselect(
        "Select Localities", filtered_stations["Locality"].unique()
    )
    if selected_localities:
        return filtered_stations[
            filtered_stations["Locality"].isin(selected_localities)
        ]
    return filtered_stations


def select_pm(filtered_stations: pd.DataFrame) -> pd.DataFrame:
    selected_pm = st.sidebar.multiselect("Select PM", filtered_stations["PM"].unique())
    if selected_pm:
        return filtered_stations[filtered_stations["PM"].isin(selected_pm)]
    return filtered_stations


def fetch_pass_analysis_data() -> None:
    station_op_id = st.sidebar.selectbox(
        "Select Station Operator ID", tollstations_df["OpID"].unique()
    )
    tag_op_id = st.sidebar.selectbox(
        "Select Tag Operator ID", tollstations_df["OpID"].unique()
    )
    date_from = st.sidebar.date_input("Select Start Date", datetime.now())
    date_to = st.sidebar.date_input("Select End Date", datetime.now())

    if st.sidebar.button("Fetch Pass Analysis"):
        date_from_str = date_from.strftime("%Y%m%d")
        date_to_str = date_to.strftime("%Y%m%d")
        pass_analysis_data = fetch_pass_analysis(
            station_op_id, tag_op_id, date_from_str, date_to_str
        )
        if pass_analysis_data:
            st.sidebar.success("Pass analysis data fetched successfully!")

            st.subheader("Pass Analysis Data")
            pass_list = pass_analysis_data.get("passList", [])
            if pass_list:
                df = pd.DataFrame(pass_list)
                st.dataframe(df)

                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Export to CSV",
                    data=csv,
                    file_name="pass_analysis.csv",
                    mime="text/csv",
                )
            else:
                st.warning("No pass data found for the selected period.")


def fetch_passes_cost_analysis() -> None:
    toll_op_id = st.sidebar.selectbox(
        "Select Toll Operator ID",
        tollstations_df["OpID"].unique(),
        key="toll_operator_select",
    )
    tag_op_id = st.sidebar.selectbox(
        "Select Tag Operator ID",
        tollstations_df["OpID"].unique(),
        key="tag_operator_select",
    )
    date_from = st.sidebar.date_input(
        "Select Start Date",
        datetime.now(),
        key="start_date_input",
    )
    date_to = st.sidebar.date_input(
        "Select End Date",
        datetime.now(),
        key="end_date_input",
    )

    if st.sidebar.button("Fetch Passes Cost"):
        date_from_str = date_from.strftime("%Y%m%d")
        date_to_str = date_to.strftime("%Y%m%d")

        passes_cost_data = fetch_passes_cost(
            toll_op_id, tag_op_id, date_from_str, date_to_str
        )

        if passes_cost_data:
            st.sidebar.success("Passes cost data fetched successfully!")

            st.subheader("Passes Cost Data")
            data = {
                "Toll Operator ID": [toll_op_id],
                "Tag Operator ID": [tag_op_id],
                "Total Passes": [passes_cost_data["nPasses"]],
                "Total Cost": [passes_cost_data["passesCost"]],
                "Period From": [date_from_str],
                "Period To": [date_to_str],
            }
            df = pd.DataFrame(data)
            st.dataframe(df)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Export to CSV",
                data=csv,
                file_name="passes_cost.csv",
                mime="text/csv",
            )
        else:
            st.warning("No passes cost data found for the selected period.")


def fetch_charges_by_analysis() -> None:
    toll_op_id = st.sidebar.selectbox(
        "Select Toll Operator ID",
        tollstations_df["OpID"].unique(),
    )
    date_from = st.sidebar.date_input(
        "Select Start Date",
        datetime.now(),
        key="start_date",
    )
    date_to = st.sidebar.date_input(
        "Select End Date",
        datetime.now(),
        key="end_date",
    )

    if st.sidebar.button("Fetch Charges By"):
        date_from_str = date_from.strftime("%Y%m%d")
        date_to_str = date_to.strftime("%Y%m%d")

        charges_by_data = fetch_charges_by(toll_op_id, date_from_str, date_to_str)

        if charges_by_data:
            st.sidebar.success("Charges by data fetched successfully!")

            st.subheader("Charges By Data")
            v_op_list = charges_by_data.get("vOpList", [])
            if v_op_list:
                df = pd.DataFrame(v_op_list)
                st.dataframe(df)

                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Export to CSV",
                    data=csv,
                    file_name="charges_by.csv",
                    mime="text/csv",
                )
            else:
                st.warning("No charges data found for the selected period.")


def fetch_tollstation_info() -> None:
    global date_from_global, date_to_global
    with st.container(border=True):
        st.markdown(
            """
            **Load passes data from starting date to ending date**.
            """
        )
        date_from = st.date_input(
            "Select Start Date",
            datetime.strptime("2022-01-01", "%Y-%m-%d"),
            key="today2",
        )
        date_to = st.date_input(
            "Select End Date",
            datetime.strptime("2022-01-14", "%Y-%m-%d"),
            key="tomorrow2",
        )

        if st.button("Load Toll Station Passes"):
            date_from_str = date_from.strftime("%Y%m%d")
            date_to_str = date_to.strftime("%Y%m%d")

            date_from_global = date_from_str
            date_to_global = date_to_str

            st.session_state.passes_data = []
            st.session_state.passes_cost_data = []

            response = requests.get(
                f"{BASE_URL}/api/getpasses/{date_from_str}/{date_to_str}"
            )

            if response.status_code != 200:
                st.error("Couldn't fetch the passes")
            else:
                tollpasses = response.json()["passes"]
                unique_passes = []
                for passes in tollpasses:
                    if passes["tollID"] not in unique_passes:
                        unique_passes.append(passes["tollID"])

                for tollid in unique_passes:
                    tollstation_revenue_data = load_tollstation_revenue(
                        tollid, date_from_str, date_to_str
                    )

                    revenue_dict = {}
                    if tollstation_revenue_data:
                        voplist = tollstation_revenue_data["vOpList"]
                        for revenue in voplist:
                            station = tollstation_revenue_data["tollOpID"]
                            if station not in revenue_dict:
                                revenue_dict[station] = 0.0
                            revenue_dict[station] += revenue["passesCost"]

                        for station, total_revenue in revenue_dict.items():
                            to_add = {"Toll Station": station, "Revenue": total_revenue}
                            if to_add not in st.session_state.passes_cost_data:
                                st.session_state.passes_cost_data.append(
                                    {"Toll Station": station, "Revenue": total_revenue}
                                )
                    else:
                        st.error("Failed to fetch passes cost data for toll station")

                    tollstation_passes_data = load_tollstation_passes(
                        tollid, date_from_str, date_to_str
                    )
                    if tollstation_passes_data:
                        to_add = {
                            "Toll Station": tollid,
                            "Passes": tollstation_passes_data["nPasses"],
                        }
                        if to_add not in st.session_state.passes_data:
                            st.session_state.passes_data.append(
                                {
                                    "Toll Station": tollid,
                                    "Passes": tollstation_passes_data["nPasses"],
                                }
                            )
                    else:
                        st.error("Failed to fetch data for toll station")

                cluster_data()
                st.success("Passes have been loaded.")


def plot_tollstation_passes() -> None:
    create_leaderboards()
    passes_revenue_bubble_chart()
    passes_treemap()
    revenue_treemap()
    passes_revenue_stacked_bar()
    plot_wheel_diagram(date_from_global, date_to_global)


def init_api_calls() -> None:
    with st.sidebar:
        st.sidebar.header("API Calls")
        fetch_pass_analysis_data()
        fetch_passes_cost_analysis()
        fetch_charges_by_analysis()
