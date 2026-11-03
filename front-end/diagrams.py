import os
import sys
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit_highcharts as hg

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "/..")))

from scheduler.cost_matrix_calculator import Companies, calculate_matrix

tollstations_df = pd.read_csv("../shared/tollstations2024.csv")


def create_leaderboards() -> None:
    if st.session_state.passes_data and st.session_state.passes_cost_data:
        passes_df = pd.DataFrame(st.session_state.passes_data)
        revenue_df = pd.DataFrame(st.session_state.passes_cost_data)

        # Merge the dataframes on "Toll Station"
        merged_df = pd.merge(passes_df, revenue_df, on="Toll Station")

        best_by_passes = merged_df.loc[merged_df["Passes"].idxmax()]
        best_by_revenue = merged_df.loc[merged_df["Revenue"].idxmax()]

        st.markdown(
            """
            <style>
            .leaderboard-card {
                border-radius: 10px;
                padding: 20px;
                background-color: #f0f2f6;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                margin-bottom: 20px;
                text-align: center;
            }
            .leaderboard-card h2 {
                color: #2c3e50;
                font-size: 24px;
                margin-bottom: 10px;
            }
            .leaderboard-card h3 {
                color: #34495e;
                font-size: 20px;
                margin-bottom: 5px;
            }
            .leaderboard-card p {
                color: #7f8c8d;
                font-size: 16px;
                margin: 0;
            }
            .metric {
                font-size: 28px;
                font-weight: bold;
                color: #27ae60;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="leaderboard-card">
                <h2>🏆 Best Toll Station by Passes</h2>
                <h3>{best_by_passes['Toll Station']}</h3>
                <p>Total Passes: <span class="metric">{best_by_passes['Passes']:,}</span></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="leaderboard-card">
                <h2>💰 Best Toll Station by Revenue</h2>
                <h3>{best_by_revenue['Toll Station']}</h3>
                <p>Total Revenue: <span class="metric">${best_by_revenue['Revenue']:,.2f}</span></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.subheader("Full Leaderboards")

        num_stations = len(merged_df)
        top_passes = merged_df.nlargest(num_stations, "Passes")
        top_revenue = merged_df.nlargest(num_stations, "Revenue")

        top_passes = top_passes.reset_index(drop=True)
        top_passes.index = top_passes.index + 1

        top_revenue = top_revenue.reset_index(drop=True)
        top_revenue.index = top_revenue.index + 1

        col1, col2 = st.columns(2, gap="large")

        with col1:
            st.subheader("Top Toll Stations by Passes")
            st.dataframe(
                top_passes.style.format({"Passes": "{:.0f}"}), height=700, width=800
            )

        with col2:
            st.subheader("Top Toll Stations by Revenue")
            st.dataframe(
                top_revenue.style.format({"Revenue": "{:.2f}"}), height=700, width=800
            )


def passes_treemap() -> None:
    if len(st.session_state.passes_data) != 0:
        passes_df = pd.DataFrame(st.session_state.passes_data)

        st.subheader("Passes Distribution by Toll Station (Treemap)")
        fig = px.treemap(
            passes_df,
            path=["Toll Station"],
            values="Passes",
            title="Passes Distribution by Toll Station",
        )
        st.plotly_chart(fig)


def revenue_treemap() -> None:
    if len(st.session_state.passes_cost_data) != 0:
        revenue_df = pd.DataFrame(st.session_state.passes_cost_data)

        st.subheader("Revenue Distribution by Toll Station (Treemap)")
        fig = px.treemap(
            revenue_df,
            path=["Toll Station"],
            values="Revenue",
            title="Revenue Distribution by Toll Station",
        )
        st.plotly_chart(fig)


def passes_revenue_stacked_bar() -> None:
    if st.session_state.passes_data and st.session_state.passes_cost_data:
        passes_df = pd.DataFrame(st.session_state.passes_data)
        revenue_df = pd.DataFrame(st.session_state.passes_cost_data)

        merged_df = pd.merge(passes_df, revenue_df, on="Toll Station")

        st.subheader("Passes and Revenue by Toll Station (Stacked Bar Chart)")
        fig = px.bar(
            merged_df,
            x="Toll Station",
            y=["Passes", "Revenue"],
            title="Passes and Revenue by Toll Station",
            labels={"value": "Count/Revenue", "variable": "Metric"},
            barmode="group",
        )
        st.plotly_chart(fig)


def passes_revenue_line_chart() -> None:
    if st.session_state.passes_data and st.session_state.passes_cost_data:
        passes_df = pd.DataFrame(st.session_state.passes_data)
        revenue_df = pd.DataFrame(st.session_state.passes_cost_data)

        merged_df = pd.merge(passes_df, revenue_df, on="Toll Station")

        st.subheader("Passes and Revenue Over Time (Line Chart)")
        fig = px.line(
            merged_df,
            x="Toll Station",
            y=["Passes", "Revenue"],
            title="Passes and Revenue Over Time",
            labels={"value": "Count/Revenue", "variable": "Metric"},
        )
        st.plotly_chart(fig)


def passes_revenue_heatmap() -> None:
    if st.session_state.passes_data and st.session_state.passes_cost_data:
        passes_df = pd.DataFrame(st.session_state.passes_data)
        revenue_df = pd.DataFrame(st.session_state.passes_cost_data)

        merged_df = pd.merge(passes_df, revenue_df, on="Toll Station")

        st.subheader("Passes and Revenue Heatmap")
        fig = px.imshow(
            merged_df[["Passes", "Revenue"]].T,
            labels=dict(x="Toll Station", y="Metric", color="Value"),
            x=merged_df["Toll Station"],
            y=["Passes", "Revenue"],
            title="Passes and Revenue Heatmap",
        )
        st.plotly_chart(fig)


def passes_revenue_bubble_chart() -> None:
    if st.session_state.passes_data and st.session_state.passes_cost_data:
        passes_df = pd.DataFrame(st.session_state.passes_data)
        revenue_df = pd.DataFrame(st.session_state.passes_cost_data)

        merged_df = pd.merge(passes_df, revenue_df, on="Toll Station")

        st.subheader("Passes vs. Revenue (Bubble Chart)")
        fig = px.scatter(
            merged_df,
            x="Passes",
            y="Revenue",
            size="Revenue",
            color="Toll Station",
            title="Passes vs. Revenue (Bubble Chart)",
            hover_name="Toll Station",
        )
        st.plotly_chart(fig)


def passes_revenue_box_plot() -> None:
    if st.session_state.passes_data and st.session_state.passes_cost_data:
        passes_df = pd.DataFrame(st.session_state.passes_data)
        revenue_df = pd.DataFrame(st.session_state.passes_cost_data)

        merged_df = pd.merge(passes_df, revenue_df, on="Toll Station")

        st.subheader("Distribution of Passes and Revenue (Box Plot)")
        fig = px.box(
            merged_df,
            y=["Passes", "Revenue"],
            title="Distribution of Passes and Revenue",
            labels={"value": "Count/Revenue", "variable": "Metric"},
        )
        st.plotly_chart(fig)


def plot_passes_revenue_scatter() -> None:
    if (
        len(st.session_state.passes_data) != 0
        and len(st.session_state.passes_cost_data) != 0
    ):
        passes_df = pd.DataFrame(st.session_state.passes_data)
        revenue_df = pd.DataFrame(st.session_state.passes_cost_data)

        merged_df = pd.merge(passes_df, revenue_df, on="Toll Station")

        st.subheader("Passes vs. Revenue Scatter Plot")
        fig = px.scatter(
            merged_df,
            x="Passes",
            y="Revenue",
            title="Passes vs. Revenue",
            hover_data=["Toll Station"],
        )
        st.plotly_chart(fig)


def plot_wheel_diagram(date_from_global: Any, date_to_global: Any) -> None:
    cost_matrix = calculate_matrix(date_from_global, date_to_global)

    data = []
    for i, from_company in enumerate(Companies):
        for j, to_company in enumerate(Companies):
            if cost_matrix[i][j] > 0:
                data.append([from_company, to_company, cost_matrix[i][j]])

    chartDef = {
        "accessibility": {
            "point": {
                "valueDescriptionFormat": "{index}. From {point.from} to {point.to}: {point.weight}."
            }
        },
        "series": [
            {
                "data": data,
                "dataLabels": {
                    "color": "#333",
                    "distance": 10,
                    "style": {"textOutline": "none"},
                    "textPath": {"attributes": {"dy": 5}, "enabled": True},
                },
                "keys": ["from", "to", "weight"],
                "name": "Dependency wheel series",
                "size": "95%",
                "type": "dependencywheel",
            }
        ],
        "title": {"text": "Cost Matrix Dependency Wheel"},
    }

    hg.streamlit_highcharts(chartDef, 640)
