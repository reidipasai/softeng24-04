import pandas as pd
import streamlit as st
from login import init_login_form
from mapbox import init_plot_mapbox
from operations import resetstations_passes, upload_passes
from tollstation_analysis import (
    fetch_tollstation_info,
    init_api_calls,
    plot_tollstation_passes,
)

if "token" not in st.session_state:
    st.session_state.token = "NULL"

if "init_account" not in st.session_state:
    st.session_state.init_account = False

st.session_state.passes_df = pd.DataFrame()
st.session_state.passes = {}

st.set_page_config(
    page_title="Gate",
    layout="wide",
)
st.image("../assets/logo.jpg", use_column_width=True)

st.write("# Welcome to TollSync: The interoperable data hub for highway networks")
st.markdown(
    """
    TollSync is an open-source live tollstation management application. It
    supports multiple-user integration, pass and cost analysis, informative
    diagrams, automatic reports, and much more!
    """
)

if __name__ == "__main__":
    init_login_form()
    resetstations_passes()
    if st.session_state.token != "NULL":
        upload_passes()
        init_plot_mapbox()
        init_api_calls()
        fetch_tollstation_info()
        if "passes_data" in st.session_state and len(st.session_state.passes_data) != 0:
            if st.button("Plot passes info"):
                plot_tollstation_passes()
        # show_tollstation_info()
