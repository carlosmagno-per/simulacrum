import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import datetime as DT
import math
import time as tm
from func.redirect import nav_page
from st_aggrid import JsCode, AgGrid, GridOptionsBuilder#, ColumnsAutoSizeMode
from st_aggrid.shared import GridUpdateMode, AgGridTheme
from database import con, cursor

# from func.connect import con, cursor


df = pd.read_sql("SELECT * FROM variaveis", con)

v3 = st.session_state.df_cliente.client_id[0]

name_v1 = st.session_state.df_cliente["Nome do Cliente"][0]

dark = df.copy()

dark = dark.rename(
    columns={
        "categoria": "Categoria",
        "ativo": "Ativo",
        "pl_aplicado": "PL Aplicado",
        "data_venc": "Data de Vencimento",
    }
)

dark = dark[dark["client_id"] == v3]

st.set_page_config(
    page_icon="invest_smart_logo.png",
    page_title="Simulador - Ativos 0.15",
    initial_sidebar_state="collapsed",
)

col1, mid, col2 = st.columns([20, 1, 16])
with col1:
    st.empty()
with col2:
    st.image(
        "investsmart_endosso_horizontal_fundopreto.png",
    )

st.header("Ativos do Cliente escolhido")

st.markdown(
    """<hr style="height:1px;border:none;color:#9966ff;background-color:#9966ff;" /> """,
    unsafe_allow_html=True,
)

colNome, colValue1 = st.columns(2)

with colNome:
    with st.container():
        st.write("Nome do cliente selecionado")

with colValue1:
    with st.container():
        st.write(fr"**{name_v1}**")

coldatatxt, coldata = st.columns(2)

with coldatatxt:
    with st.container():
        st.write("Data de entrada para um novo ativo")

with coldata:
    with st.container():
        st.write(DT.datetime.strftime(DT.datetime.today(), "%d-%b-%Y"))

# st.table(dark)

gridOptions = GridOptionsBuilder.from_dataframe(
    dark[
        [
            # "client_id",
            "Categoria",
            "Ativo",
            "PL Aplicado",
            "Data de Vencimento",
            # "shelf_id",
        ]
    ]
)

gridOptions.configure_selection(
    selection_mode="single", use_checkbox=True, pre_selected_rows=[0]
)


gb = gridOptions.build()

mycntnr = st.container()
with mycntnr:
    htmlstr = f"<p style='background-color: #9966ff; color: #000000; font-size: 16px; border-radius: 7px; padding-left: 8px; text-align: center'>Tabela de Ativos</style></p>"
    st.markdown(htmlstr, unsafe_allow_html=True)

    dta = AgGrid(
        dark,
        gridOptions=gb,
        height=400,
        allow_unsafe_jscode=True,
        theme=AgGridTheme.ALPINE,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW,
        reload_data=True,
    )

st.markdown(
    """
    <hr style="height:1px;border:none;color:#9966ff;background-color:#9966ff;" /> 
    <p > Deseja incluir um novo ativo ?</p>
    """,
    unsafe_allow_html=True,
)

st.session_state["df_ativo"] = pd.DataFrame(dta["selected_rows"])

if "button1" not in st.session_state:
    st.session_state["button1"] = False

botao1, botao2 = st.columns(2)

with botao1:
    if st.button("Incluir um novo ativo InvestSmart"):
        nav_page("novo_ativo")

with botao2:
    if st.button("Incluir um novo ativo Be.Smart"):
        st.session_state["button1"] = not st.session_state["button1"]
    if st.session_state["button1"]:
        checks = st.radio(
            "Qual tipo de produto será Incluido:",
            [
                "Cambio",
                "Protect",
                "Credito",
                "Diversificações",
                "Empresas",
            ],
            horizontal=True,
        )
        if st.button("Incluir esse tipo de ativo"):
            nav_page("novo_ativo")

st.markdown(
    """<hr style="height:1px;border:none;color:#9966ff;background-color:#9966ff;" /> """,
    unsafe_allow_html=True,
)


botao3, botao4, botao5 = st.columns(3)
with botao3:
    if st.button("Voltar"):
        nav_page("assessor_cliente")

with botao4:
    if st.button("Editar um Ativo"):
        if st.session_state["df_ativo"].empty:
            st.error("Não foi selecionado um ativo")
        else:
            nav_page("edit_ativo")

with botao5:
    if st.button("Deletar um Ativo"):
        if st.session_state["df_ativo"].empty:
            st.error("Não foi selecionado um ativo")
        else:
            vers = int(st.session_state.df_ativo.ativo_id[0])
            cursor.execute("DELETE FROM variaveis WHERE ativo_id = ?", (vers,))
            con.commit()
            st.success("O ativo foi deletado com sucesso")
            tm.sleep(1)
            st._rerun()


st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
    footer {visibility: hidden;}
</style>
""",
    unsafe_allow_html=True,
)
