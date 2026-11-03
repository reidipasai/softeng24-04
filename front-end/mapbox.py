from typing import Optional

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
from tollstation_analysis import (
    fetch_tollstations,
    select_localities,
    select_operators,
    select_pm,
    select_roads,
)

GOOGLE_MAPS_API_KEY = ""

tollstations_df = pd.read_csv("../shared/tollstations2024.csv")


def plot_map(
    with_traffic: bool = False, filtered_stations: Optional[pd.DataFrame] = None
) -> None:
    with st.container(border=True):
        if filtered_stations is None:
            filtered_stations = tollstations_df

        map = folium.Map(location=[38.500, 26.500], zoom_start=7)

        for _, station in filtered_stations.iterrows():
            folium.Marker(
                [station["Lat"], station["Long"]],
                popup=f"<b>{station['Name']}</b>",
                icon=folium.Icon(icon="road", prefix="fa"),
            ).add_to(map)

        if "clustered_data" in st.session_state:
            clustered_data = st.session_state.clustered_data
            color_map = {0: "green", 1: "yellow", 2: "red"}
            for _, row in clustered_data.iterrows():
                Lat = None
                Long = None

                for _, rrow in filtered_stations.iterrows():
                    if rrow["TollID"] == row["Toll Station"]:
                        Lat = rrow["Lat"]
                        Long = rrow["Long"]
                        break

                if Lat is not None and Long is not None:
                    folium.CircleMarker(
                        location=[Lat, Long],
                        radius=20,  # Scale size based on pass count
                        color=color_map[row["Cluster"]],
                        fill=True,
                        fill_color=color_map[row["Cluster"]],
                        fill_opacity=0.7,
                        popup=f"{row['Toll Station']}<br>Passes: {row['Passes']}<br>Color: {color_map[row['Cluster']]}",
                    ).add_to(map)

        if with_traffic:
            traffic_layer = folium.TileLayer(
                tiles=f"https://mt1.google.com/vt/lyrs=h,traffic&x={{x}}&y={{y}}&z={{z}}&key={GOOGLE_MAPS_API_KEY}",
                attr="Google Traffic Data",
                name="Traffic",
                overlay=True,
                control=True,
            )
            traffic_layer.add_to(map)

        folium.LayerControl().add_to(map)

        st_folium(map, height=800, width="100%", use_container_width=True)


def init_plot_mapbox() -> None:
    st.title("Toll Stations and Traffic Map")
    st.markdown(
        """
        This interactive map allows you to view toll stations and overlay real-time traffic data in the selected area.
        You can fetch the toll stations and toggle traffic visibility.
        """
    )

    with st.sidebar:
        st.sidebar.header("Options")
        if st.button("Fetch Toll Stations"):
            fetch_tollstations()

        if "show_traffic" not in st.session_state:
            st.session_state.show_traffic = False

        if "show_map" not in st.session_state:
            st.session_state.show_map = False

        toggle_map = st.sidebar.button(
            "Hide Map" if st.session_state.show_map else "Show Map"
        )

        toggle_traffic = st.sidebar.button(
            "Hide Traffic" if st.session_state.show_traffic else "Show Traffic"
        )

        if toggle_map:
            st.session_state.show_map = not st.session_state.show_map

        if toggle_traffic:
            st.session_state.show_traffic = not st.session_state.show_traffic

        filtered_stations = select_operators()
        filtered_stations = select_roads(filtered_stations)
        filtered_stations = select_localities(filtered_stations)
        filtered_stations = select_pm(filtered_stations)

    if st.session_state.show_map:
        plot_map(
            with_traffic=st.session_state.show_traffic,
            filtered_stations=filtered_stations,
        )

    st.markdown(
        """
        - **Toll Stations:** This will show all the toll stations based on your data.
        - **Traffic Layer:** You can toggle the visibility of real-time traffic data.
        - **Map Interactivity:** Zoom and pan around the map to explore more.
        """
    )
