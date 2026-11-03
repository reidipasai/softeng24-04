import pandas as pd
import requests  # type: ignore
import streamlit as st
from sklearn.cluster import KMeans

BASE_URL = "http://127.0.0.1:9115"


def cluster_data() -> None:
    if st.session_state.passes_data and st.session_state.passes_cost_data:
        if "clustered_data" not in st.session_state:
            st.session_state.clustered_data = None

        passes_df = pd.DataFrame(st.session_state.passes_data)
        revenue_df = pd.DataFrame(st.session_state.passes_cost_data)

        merged_df = pd.merge(passes_df, revenue_df, on="Toll Station")

        # Select only numeric columns for clustering
        X = merged_df[["Passes", "Revenue"]].values

        # Perform KMeans clustering with 3 clusters
        kmeans = KMeans(n_clusters=3, random_state=42)
        merged_df["Cluster"] = kmeans.fit_predict(X)

        # Map clusters to colors
        cluster_colors = {0: "red", 1: "yellow", 2: "green"}

        # Assign colors based on cluster
        merged_df["Color"] = merged_df["Cluster"].map(cluster_colors)

        st.session_state.clustered_data = merged_df


def upload_passes() -> None:
    if "uploaded_file" not in st.session_state:
        st.session_state.uploaded_file = None

    uploaded_file = st.sidebar.file_uploader(
        "Upload passes CSV", type=["csv"], key="file_uploader"
    )

    if uploaded_file is not None:
        st.session_state.uploaded_file = uploaded_file

    if st.session_state.uploaded_file is not None:
        if st.sidebar.button("Upload Passes"):
            try:
                file_contents = st.session_state.uploaded_file.read()
                passes_df = pd.read_csv(pd.io.common.BytesIO(file_contents))
                csv_data = passes_df.to_csv(index=False)

                response = requests.post(
                    f"{BASE_URL}/api/admin/addpasses?format=csv",
                    data=csv_data.encode("utf-8"),  # Ensure bytes are sent
                    headers={
                        "Content-Type": "text/csv",
                        "X-OBSERVATORY-AUTH": st.session_state.token,
                    },
                )

                if response.status_code == 200:
                    st.success("Passes uploaded successfully!")
                    st.session_state.uploaded_file = None
                else:
                    st.error(
                        f"Failed to upload passes: {response.json().get('info', 'Unknown error')}"
                    )
            except Exception as e:
                st.error(f"Error processing the uploaded file: {e}")


def resetstations_passes() -> None:
    with st.sidebar:
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Reset stations"):
                data = pd.read_csv(
                    "../shared/tollstations2024.csv", encoding="utf-8"
                ).to_json(orient="records")
                response = requests.post(
                    f"{BASE_URL}/api/admin/resetstations",
                    data=data,
                    headers={"X-OBSERVATORY-AUTH": st.session_state.token},
                )
                if response.status_code == 400:
                    st.warning(
                        "Only Admin users can access this! Please make sure that you login as an Admin"
                    )
                elif response.status_code != 200:
                    st.warning("Stations did not load correctly. Please try again!")
                else:
                    st.info("Stations reset successfully!")

        with col2:
            if st.button("Reset passes"):
                response = requests.post(
                    f"{BASE_URL}/api/admin/resetpasses",
                    headers={"X-OBSERVATORY-AUTH": st.session_state.token},
                )
                if response.status_code == 400:
                    st.warning(
                        "Only Admin users can access this! Please make sure that you login as an Admin"
                    )
                elif response.status_code != 200:
                    st.warning("Passes did not reset correctly. Please try again!")
                else:

                    st.info("Passes reset successfully!")
