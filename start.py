import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import datetime as DT
import math
import time as tm
from func.redirect import nav_page
import sqlite3


df = pd.read_excel("sigla.xlsx")

sigla = df["SIGLA"].unique()


st.set_page_config(
    page_icon="invest_smart_logo.png",
    page_title="Simulador 0.15",
    initial_sidebar_state="collapsed",
    # layout="wide",
)


# available_views = ["report"]
# if view not in available_views:
#     # I don't know which view do you want. Beat it.
#     st.warning("404 Error")
#     st.stop()
query_params = st.experimental_get_query_params()
username = query_params.get("username", None)[0]
logged_in = False
if username in sigla:
    logged_in = True

if not logged_in:
    # If credentials are invalid show a message and stop rendering the webapp
    st.warning("Credenciais erradas")
    st.stop()

nome = df[df["SIGLA"] == username].NOME.unique()[0]

st.header("SIMULADOR")

st.session_state["usuario"] = username
st.session_state["assessor"] = nome

st.subheader(f"BEM VINDO/A, {nome}")

if st.button("Iniciar a ferramenta"):
    nav_page("assessor_cliente")


no_sidebar_style = """
    <style>
        div[data-testid="stSidebarNav"] {display: none;}
        footer {visibility: hidden;}
    </style>
"""
st.markdown(no_sidebar_style, unsafe_allow_html=True)


# http://localhost:8501/?username=BRGK
