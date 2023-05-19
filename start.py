import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import datetime as DT
import math
import time as tm
from func.redirect import nav_page
import sqlite3

from msal_streamlit_authentication import msal_authentication

# df = pd.read_excel("sigla_v2.xlsx")

# sigla = df["SIGLA"].unique()


st.set_page_config(
    page_icon="invest_smart_logo.png",
    page_title="Simulador 0.25",
    initial_sidebar_state="collapsed",
    # layout="wide",
)

st.title('Simulador, Página de Login')

text,botao =st.columns(2)

with botao:

    login_token = msal_authentication(
        auth={
            "clientId": "38dcd06e-ad0c-4509-ae3f-2690ff4e3362",
            "authority": "https://login.microsoftonline.com/94cd8921-8f5c-4862-83a8-aeaab06c4082",
            "redirectUri": "/",
            "postLogoutRedirectUri": "/"
        }, # Corresponds to the 'auth' configuration for an MSAL Instance
        cache={
            "cacheLocation": "sessionStorage",
            "storeAuthStateInCookie": True
        } # Corresponds to the 'cache' configuration for an MSAL Instance
    )


with text:
    if login_token ==None:
        st.write('')
        st.write('')
        # st.write('')
        # st.write('')
        st.write(
        fr'<p style="font-size:26px;">Por favor clique no botão ao lado, para entrar na ferramenta com seu email da empresa</p>',
        unsafe_allow_html=True,
    )
        #st.write("Por favor clique no botão ao lado, para entrar na ferramenta com seu email da empresa")
        st.stop()
    else:
        st.write('')
        st.write('')
        st.write('')
        st.write('')
        value=login_token['account']['name']
        st.write(
        f'<p style="font-size:26px;">BEM VINDO/A,{value}</p>',
        unsafe_allow_html=True,
    )
        #st.subheader(f"BEM VINDO/A, {login_token['account']['name']}")

nome=login_token['account']['name']
username=login_token['account']['username']
#st.write(f"BEM VINDO/A, {login_token['account']['name']}")
#st.write("Recevied login token:", login_token)

#st.write("Recevied login name:", nome)

#st.write("Recevied login username:", username)

# available_views = ["report"]
# if view not in available_views:
#     # I don't know which view do you want. Beat it.
#     st.warning("404 Error")
#     st.stop()
# query_params = st.experimental_get_query_params()
# username = query_params.get("username", None)[0]
# logged_in = False
# if username in sigla:
#     logged_in = True

# if not logged_in:
#     # If credentials are invalid show a message and stop rendering the webapp
#     st.warning("Credenciais erradas")
#     st.stop()

#nome = df[df["SIGLA"] == username].NOME.unique()[0]

#st.header("SIMULADOR")

st.session_state["usuario"] = username
st.session_state["assessor"] = nome
st.session_state["logout"] = login_token

st.subheader(f"Você está Utilizando o Email, {username}")

st.write('')
st.write('')
# if st.button("Iniciar a ferramenta"):
#     nav_page("assessor_cliente")

if st.button("Iniciar a ferramenta"):
    nav_page("wide_project")

no_sidebar_style = """
    <style>
        div[data-testid="stSidebarNav"] {display: none;}
        footer {visibility: hidden;}
    </style>
"""
st.markdown(no_sidebar_style, unsafe_allow_html=True)


# http://localhost:8501/?username=BRGK
