import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import datetime as DT
import math
import time as tm
from func.redirect import nav_page
import pymysql
from sqlalchemy import create_engine
from database import moeda, base_df, PositivadorBitrix
import locale
import requests

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")


st.set_page_config(
    page_icon="invest_smart_logo.png",
    page_title="Simulador - Edit Ativos 0.25",
    initial_sidebar_state="collapsed",
    layout="wide",
)

col1, mid, col2 = st.columns([20, 2, 4])
with col1:
    st.header("Visualizando um Ativo")
with col2:
    st.image("investsmart_endosso_horizontal_fundopreto.png", width=270)
    esquerda, direita  = st.columns([5, 4])
    with direita:
        if st.button('Logout',key='logout5'):
            st.session_state["logout"] =None
            if st.session_state["logout"]==None:
                nav_page('')

    
st.markdown(
    """<hr style="height:1px;border:none;color:#9966ff;background-color:#9966ff;" /> """,
    unsafe_allow_html=True,
)
#st.dataframe(st.session_state.df_ativo1)
try:    
    v4 = int(st.session_state.df_ativo1.ativo_id[0])
    v1_categ = st.session_state.df_ativo1.Categoria.iloc[0]
    v1_ativo = st.session_state.df_ativo1.Ativo.iloc[0]
    v1_data = st.session_state.df_ativo1["Data de Vencimento"].iloc[0]
    v1_data_inicio = st.session_state.df_ativo1["Data de Início"].iloc[0]
    v1_pl_apl = (
        st.session_state.df_ativo1["PL Aplicado"]
        .iloc[0][3:]
        .replace(".", "")
        .replace(",", ".")
    )
    v1_retorno = st.session_state.df_ativo1.retorno.iloc[0]
    v1_repasse = st.session_state.df_ativo1.repasse.iloc[0]
    v1_roa_head = st.session_state.df_ativo1.roa_head.iloc[0]
    v1_roa_rec = st.session_state.df_ativo1.roa_rec.iloc[0]
except:
    v4 = int(st.session_state.df_ativo.ativo_id[0])
    v1_categ = st.session_state.df_ativo.Categoria.iloc[0]
    v1_ativo = st.session_state.df_ativo.Ativo.iloc[0]
    v1_data = st.session_state.df_ativo["Data de Vencimento"].iloc[0]
    v1_data_inicio = st.session_state.df_ativo["Data de Início"].iloc[0]
    v1_pl_apl = (
        st.session_state.df_ativo["PL Aplicado"]
        .iloc[0][3:]
        .replace(".", "")
        .replace(",", ".")
    )
    v1_retorno = st.session_state.df_ativo.retorno.iloc[0]
    v1_repasse = st.session_state.df_ativo.repasse.iloc[0]
    v1_roa_head = st.session_state.df_ativo.roa_head.iloc[0]
    v1_roa_rec = st.session_state.df_ativo.roa_rec.iloc[0]
roa_reps = float(v1_repasse)
prem, table = st.columns(2)

with prem:
    st.subheader("**Premissas**")

    def disable():
        st.session_state.disabled = False
    
    if "disabled" not in st.session_state:
        st.session_state.disabled = True

        
    face = pd.read_excel("bd_base_v3.xlsx")
    face["Categoria"] = face["Categoria"].apply(lambda x: x.replace("_", " "))
    face["ROA Cabeça"] = face["ROA Cabeça"] * 100.0
    face["Roa Recorrente"] = face["Roa Recorrente"] * 100.0

    categoria_list = list(face.Categoria.unique())
    good_categ = ["Fundos","Previdencia"]
    colNome1, colValue1 = st.columns(2)

    with colNome1:
        categoria = st.selectbox(
            "Categoria: ", face.Categoria.unique(), index=categoria_list.index(v1_categ),disabled=st.session_state["disabled"],  
        )
    try:
        ind = list(face.PRODUTOS[face["Categoria"] == categoria].unique()).index(
            v1_ativo
        )

        with colValue1:
            ativo = st.selectbox(
                "Ativo: ",
                list(face.PRODUTOS[face["Categoria"] == categoria].unique()),
                index=ind,
                on_change=disable,
                disabled=st.session_state.disabled, 
                 
            )
    except:
        with colValue1:
            ativo = st.selectbox(
                "Ativo: ",
                list(face.PRODUTOS[face["Categoria"] == categoria].unique()),
                on_change=disable,
                disabled=st.session_state.disabled, 
                 
            )
        
############################################################################################        
#####################################LORD OF THE GAME#######################################
############################################################################################
    # colNome2, colValue2 = st.columns(2)


    # with colNome2:
    pl_apl = st.number_input(
        "PL Aplicado (R$): ",
        min_value=0.0,
        format="%f",
        value=float(v1_pl_apl),
        step=1000.0,
        on_change=disable,
        disabled=st.session_state.disabled, 
            
    )
    st.text("R$" + locale.currency(pl_apl, grouping=True, symbol=None))


    if categoria in good_categ:
        subcategoria = st.selectbox(
            "Subcategoria: ",
            face.sort_values(by="Subcategoria").Subcategoria[face["Categoria"] == categoria].unique(),
            on_change=disable,
            disabled=st.session_state.disabled, 
        )

    colNome3, colValue3 = st.columns(2)
    with colNome3:
        data_inicial = st.date_input(
            "Data de Início: ",
            # min_value=DT.date.today(),
            value=DT.datetime.strptime(v1_data_inicio[:10], "%Y-%m-%d"),
            on_change=disable,
            disabled=st.session_state.disabled, 
             
        )

    with colValue3:
        data = st.date_input(
            "Data de Vencimento: ",
            # min_value=DT.date.today(),
            value=DT.datetime.strptime(v1_data[:10], "%Y-%m-%d"),
            on_change=disable,
            disabled=st.session_state.disabled, 
             
        )

    colRoa_rec, colroa_head= st.columns(2)

    with colRoa_rec:
        roa_rec = st.number_input(
            "ROA Recorrente (%): ",
            min_value=0.0,
            format="%.2f",
            value=float(v1_roa_rec),
            max_value=100.0,
            step=0.1,
            on_change=disable,
            disabled=st.session_state.disabled, 
             
        )

    with colroa_head:
        roa_head = st.number_input(
            "ROA Cabeça (%): ",
            min_value=0.0,
            max_value=100.0,
            value=float(v1_roa_head),
            format="%.2f",
            step=0.01,
            on_change=disable,
            disabled=st.session_state.disabled, 
             
        )
    if categoria == "Renda Fixa":
        retorno = st.number_input(
        "Retorno Esperado a.a. (%): ",
        min_value=0.0,
        max_value=100.0,
        value=float(v1_retorno),
        format="%f",
        step=1.0,
        on_change=disable,
        disabled=st.session_state.disabled, 
            
    )
    else:
        retorno = 0

  
    edit, salve_v3, espaco_10= st.columns([5,5,15])
    with edit:
        if st.button("Editar"):
            st.session_state["disabled"] = not st.session_state["disabled"] 



v3 = int(st.session_state.df_cliente.client_id[0])

with table:
    st.header("Fluxo de Comissão")
    if data > data_inicial:

        dataframe = base_df(
            data, data_inicial, pl_apl, retorno, roa_head, roa_rec, roa_reps
        )

        hide_dataframe_row_index = """
                    <style>
                    .row_heading.level0 {display:none}
                    .blank {display:none}
                    </style>
                    """

        st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)

        #st.dataframe(dataframe)
        st.dataframe(dataframe[['Mês','Roa/Mês(%)','Faturamento','Imposto','Receita Líquida', 'Resultado assessor']])

        with salve_v3:
            if st.button("Salvar"):

                url = "https://"+st.secrets.domain+"rest/"+st.secrets.bignumber+"/"+st.secrets.cod_shhh+"/crm.deal.update.json?"+st.secrets.id+f"={v4}&fields["+st.secrets.VAR4+f"]={categoria}&fields["+st.secrets.VAR5+f"]={ativo}&fields["+st.secrets.VAR6+f"]={roa_head}&fields["+st.secrets.VAR7+f"]={roa_rec}&fields["+st.secrets.VAR8+f"]={pl_apl}&fields["+st.secrets.VAR9+f"]={data_inicial}&fields["+st.secrets.VAR10+f"]={data}&fields["+st.secrets.VAR11+f"]={v3}&fields["+st.secrets.VAR12+f"]=INVESTSMART&fields["+st.secrets.VAR13+f"]={retorno}&fields["+st.secrets.VAR14+f"]={roa_reps}&fields["+st.secrets.category+f"]="+st.secrets.arabian

                payload = {}
                headers = {
                'Cookie': 'BITRIX_SM_SALE_UID=0'
                }

                response = requests.request("POST", url, headers=headers, data=payload)

                st.success("O ativo foi editado com sucesso")
                tm.sleep(1)
                with st.spinner("Redirecionando o Assessor para a Página de Ativos"):
                    tm.sleep(1)
                nav_page("cliente_wide")
    else:
        st.error("Data de vencimento menor que a data de Início.")

st.markdown(
    """<hr style="height:1px;border:none;color:#9966ff;background-color:#9966ff;" /> """,
    unsafe_allow_html=True,
)

if st.button("Voltar"):
    nav_page("cliente_wide")

st.markdown(
    """
<style>
    div [data-testid="stToolbar"] {display: none;}
    #MainMenu {visibility: hidden;}
    [data-testid="collapsedControl"] {
        display: none
    }
    footer {visibility: hidden;}
</style>
""",
    unsafe_allow_html=True,
)

# st.markdown(
#     """
# <style>
#     .st-bw {
#     background-color: rgb(63, 63, 63);
#     }
#     [data-testid="collapsedControl"] {
#         display: none
#     }
#     footer {visibility: hidden;}

#     .css-qriz5p:hover:enabled, .css-qriz5p:focus:enabled {
#     color: rgb(255, 255, 255);
#     background-color: rgb(153, 102, 255);
#     transition: none 0s ease 0s;
#     outline: none;
# }
#     img {
#     background-color: rgb(18, 19, 18);
#     }

# </style>
# """,
#     unsafe_allow_html=True,
# )
