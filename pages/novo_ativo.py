import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import datetime as DT
import math
import time as tm
from func.redirect import nav_page
from sqlalchemy import create_engine
from database import moeda, base_df, PositivadorBitrix
import locale
import streamlit.components.v1 as components
import plotly.express as px
import requests


locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")




st.set_page_config(
    page_icon="invest_smart_logo.png",
    page_title="Simulador - Novo Ativos 0.25",
    initial_sidebar_state="collapsed",
    layout="wide",
)
col1, mid, col2 = st.columns([20, 2, 4])
with col1:
    st.header("Incluindo um Novo ativo para o Cliente")
with col2:
    st.image("investsmart_endosso_horizontal_fundopreto.png", width=270)
    esquerda, direita  = st.columns([5, 4])
    with direita:
        if st.button('Logout',key='logout4'):
            st.session_state["logout"] =None
            if st.session_state["logout"]==None:
                nav_page('')


st.markdown(
    """<hr style="height:1px;border:none;color:#9966ff;background-color:#9966ff;" /> """,
    unsafe_allow_html=True,
)

prem, table = st.columns(2)
with prem:
    st.subheader("**Premissas**")

    face = pd.read_excel("bd_base_v3.xlsx")
    face["Categoria"] = face["Categoria"].apply(lambda x: x.replace("_", " "))
    face["ROA Cabeça"] = face["ROA Cabeça"] * 100.0
    face["Roa Recorrente"] = face["Roa Recorrente"] * 100.0
    v3 = int(st.session_state.df_cliente.client_id[0])
    name_v1 = st.session_state.df_cliente["Nome do Cliente"][0]

    # st.write(v3)
    # st.write(name_v1)
    good_categ = ["Fundos","Previdencia"]
    

    colNome1, colValue1 = st.columns(2)

    with colNome1:
        categoria = st.selectbox(
            "Categoria: ",
            face.sort_values(by="Categoria").Categoria.unique(),
        )
    if categoria in good_categ:
        with colValue1:
            subcategoria = st.selectbox(
                "Subcategoria: ",
                face.sort_values(by="Subcategoria").Subcategoria[face["Categoria"] == categoria].unique(),
            )  
            

        colNome2, colValue2 = st.columns(2)

        with colNome2:
            ativo = st.selectbox(
                    "Ativo: ", list(face.sort_values(by="PRODUTOS").PRODUTOS[(face["Categoria"] == categoria) & (face["Subcategoria"] == subcategoria)].unique())
                )
            

        with colValue2:
            pl_apl = st.number_input(
                "PL Aplicado (R$): ",
                min_value=0.0,
                format="%f",
                value=3000000.0,
                step=1000.0,
            )
            st.text("R$" + locale.currency(pl_apl, grouping=True, symbol=None))
     

        colNome3, colValue3 = st.columns(2)
        with colNome3:
            data_inicial = st.date_input("Data de Início: ", min_value=DT.date.today())

        with colValue3:
            data = st.date_input("Data de Vencimento: ", min_value=DT.date.today())

        colroa_head, colRoa_rec = st.columns(2)
        #colroa_head, colRoa_rec, colRepasse = st.columns(3)

        with colRoa_rec:
            roa_rec = st.number_input(
                "ROA Recorrente (%): ",
                min_value=0.0,
                format="%.2f",
                value=float(face["Roa Recorrente"][face["PRODUTOS"] == ativo]),
                max_value=100.0,
                step=0.1,
            )

        with colroa_head:
            roa_head = st.number_input(
                "ROA Cabeça (%): ",
                min_value=0.0,
                max_value=100.0,
                value=float(face["ROA Cabeça"][face["PRODUTOS"] == ativo]),
                format="%.2f",
                step=0.01,
            )

    
        roa_reps = 50.0
        retorno= 0.0
        
    
    else:
        with colValue1:
            ativo = st.selectbox(
                    "Ativo: ", list(face.sort_values(by="PRODUTOS").PRODUTOS[(face["Categoria"] == categoria)].unique())
                )
            
        pl_apl = st.number_input(
            "PL Aplicado (R$): ",
            min_value=0.0,
            format="%f",
            value=3000000.0,
            step=1000.0,
        )
        st.text("R$" + locale.currency(pl_apl, grouping=True, symbol=None))

        colNome3, colValue3 = st.columns(2)
        with colNome3:
            data_inicial = st.date_input("Data de Início: ", min_value=DT.date.today())

        with colValue3:
            data = st.date_input("Data de Vencimento: ", min_value=DT.date.today())

        colroa_head, colRoa_rec = st.columns(2)
        #colroa_head, colRoa_rec, colRepasse = st.columns(3)

        with colRoa_rec:
            roa_rec = st.number_input(
                "ROA Recorrente (%): ",
                min_value=0.0,
                format="%.2f",
                value=float(face["Roa Recorrente"][face["PRODUTOS"] == ativo]),
                max_value=100.0,
                step=0.1,
            )

        with colroa_head:
            roa_head = st.number_input(
                "ROA Cabeça (%): ",
                min_value=0.0,
                max_value=100.0,
                value=float(face["ROA Cabeça"][face["PRODUTOS"] == ativo]),
                format="%.2f",
                step=0.01,
            )
        roa_reps = 50.0
        retorno= 0.0

st.markdown(
    """<hr style="height:1px;border:none;color:#9966ff;background-color:#9966ff;" /> """,
    unsafe_allow_html=True,
)

volte, salve_v2, espaco_10= st.columns([5,5,15])
with volte:
    if st.button("Voltar"):
        nav_page("cliente_wide")

with table:
    st.subheader("**Fluxo de Comissão**")
    if data > data_inicial:

        dataframe = base_df(
            data, data_inicial, pl_apl, retorno, roa_head, roa_rec, roa_reps
        )

        st.dataframe(dataframe)


        with salve_v2:
            if st.button("Salvar"):
     
                url = "https://"+st.secrets.domain+"rest/"+st.secrets.bignumber+"/"+st.secrets.cod_shhh+"/crm.deal.add.json?fields["+st.secrets.VAR4+f"]={categoria}&fields["+st.secrets.VAR5+f"]={ativo}&fields["+st.secrets.VAR6+f"]={roa_head}&fields["+st.secrets.VAR7+f"]={roa_rec}&fields["+st.secrets.VAR8+f"]={pl_apl}&fields["+st.secrets.VAR9+f"]={data_inicial}&fields["+st.secrets.VAR10+f"]={data}&fields["+st.secrets.VAR11+f"]={v3}&fields["+st.secrets.VAR12+f"]=INVESTSMART&fields["+st.secrets.VAR13+f"]={retorno}&fields["+st.secrets.VAR14+f"]={roa_reps}&fields["+st.secrets.category+"]="+st.secrets.arabian

                payload = {}
                headers = {
                'Cookie': 'BITRIX_SM_SALE_UID=0; qmb=0.'
                }

                response = requests.request("POST", url, headers=headers, data=payload)
                st.success("O ativo foi editado com sucesso")
                tm.sleep(1)
                with st.spinner("Redirecionando o Assessor para a Página de Ativos"):
                    tm.sleep(1)
                nav_page("cliente_wide")
    else:
        st.error("Data de vencimento tem que ser maior que a data de Início.")

st.markdown(
    """
<style>
    #MainMenu {visibility: hidden;}
    [data-testid="collapsedControl"] {
        display: none
    }
    footer {visibility: hidden;}
</style>
""",
    unsafe_allow_html=True,
)
