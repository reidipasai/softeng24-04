import os
import sys

import requests  # type: ignore
import streamlit as st

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../back-end/"))
)
from database.models import Session
from mongoengine import connect

connect(
    "test", host="mongodb://localhost:27017/test"
)  # TODO, FUTURE, FIXME: This needs to go away, if we have time in the future, we should make something with session state

BASE_URL = "http://127.0.0.1:9115"


def init_login_form() -> None:
    """
    initializes the login form. Supports login and logout from the sidebar
    """
    with st.sidebar:
        with st.form(key="login"):
            username = st.text_input(
                "username", label_visibility="visible", placeholder="Username"
            )
            password = st.text_input(
                "password",
                label_visibility="visible",
                placeholder="Password",
                type="password",
            )

            col1, col2 = st.columns([1, 1])
            with col1:
                login_button = st.form_submit_button(label="Login")
            with col2:
                logout_button = st.form_submit_button(label="Logout")

            if login_button:
                if username and password:
                    search_already_logged = Session.objects(username=username).first()
                    if search_already_logged is not None:
                        print(search_already_logged)
                        st.session_state.token = search_already_logged["token"]
                        st.session_state.username = username
                        st.session_state.password = password
                        st.success(
                            f"Succesfully logged in. User's token: {st.session_state.token}"
                        )
                    else:
                        response = requests.post(
                            f"{BASE_URL}/api/login",
                            json={"username": username, "password": password},
                        )
                        if response.status_code == 200:
                            st.session_state.token = response.json()["token"]
                            st.session_state.username = username
                            st.session_state.password = password
                            st.success(
                                f"Succesfully logged in. User's token: {st.session_state.token}"
                            )

                        elif st.session_state.token != "NULL":
                            st.warning("Already logged in! Please logout")
                        else:
                            st.warning("Wrong username or password")
                else:
                    st.warning(
                        "Please make sure you provided both a username and a password"
                    )

            if logout_button:
                if "username" in st.session_state and "password" in st.session_state:
                    response = requests.post(
                        f"{BASE_URL}/api/logout",
                        headers={"X-OBSERVATORY-AUTH": st.session_state.token},
                    )
                    if response.status_code != 200:
                        st.warning("Error while logging out")
                    else:
                        st.info("Succesfully logged out!")
                else:
                    st.warning("User is not logged in!")
