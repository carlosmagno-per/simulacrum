import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import datetime as DT
import math
import time as tm
from func.redirect import nav_page
from st_aggrid import JsCode, AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
from st_aggrid.shared import GridUpdateMode, AgGridTheme
from database import con, cursor

# from func.connect import con, cursor


df = pd.read_sql("SELECT * FROM cliente", con)

dark = df.copy()
dark = dark.rename(
    columns={
        "nome_client": "Nome do Cliente",
        "data_cliente": "Data de entrada do Cliente",
    }
)
id_v1 = st.session_state.usuario

dark = dark[dark["sigla"] == id_v1]

st.set_page_config(
    page_icon="invest_smart_logo.png",
    page_title="Simulador - Clientes 0.15",
    initial_sidebar_state="collapsed",
)

col1, mid, col2 = st.columns([20, 1, 16])
with col1:
    st.empty()
with col2:
    st.image(
        "investsmart_endosso_horizontal_fundopreto.png",
    )

st.header("Clientes do Assessor")

st.markdown(
    """<hr style="height:1px;border:none;color:#9966ff;background-color:#9966ff;" /> """,
    unsafe_allow_html=True,
)

colNome, colValue1 = st.columns(2)

with colNome:
    with st.container():
        st.write("Clientes do Assessor:")

with colValue1:
    with st.container():
        st.write(fr"**{st.session_state.assessor}**")
#####################################
#####################################


gridOptions = GridOptionsBuilder.from_dataframe(
    dark[["Nome do Cliente", "Data de entrada do Cliente"]]
)

gridOptions.configure_selection(
    selection_mode="single", use_checkbox=True, pre_selected_rows=[0]
)


gb = gridOptions.build()

mycntnr = st.container()
with mycntnr:
    htmlstr = f"<p style='background-color: #9966ff; color: #000000; font-size: 16px; border-radius: 7px; padding-left: 8px; text-align: center'>Tabela de Clientes</style></p>"
    st.markdown(htmlstr, unsafe_allow_html=True)

    dta = AgGrid(
        dark,
        gridOptions=gb,
        height=300,
        allow_unsafe_jscode=True,
        theme=AgGridTheme.ALPINE,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW,
        reload_data=True,
    )
    # st.experimental_rerun()

# st.experimental_data_editor(
#     dark[["Nome do Cliente", "Data de entrada do Cliente"]],
#     use_container_width=True,
#     num_rows="dynamic",
#     on_change="dance"
#     # disabled=True,
# )

# st.table(dta.data)

#####################################
#####################################

st.markdown(
    """<hr style="height:1px;border:none;color:#9966ff;background-color:#9966ff;" /> """,
    unsafe_allow_html=True,
)

sql = "INSERT INTO cliente (sigla, nome_client, data_cliente) VALUES (?, ?, ?)"
today = DT.datetime.strftime(DT.datetime.today(), "%Y-%m-%d")
hoje = today


if "button1" not in st.session_state:
    st.session_state["button1"] = False

if "button2" not in st.session_state:
    st.session_state["button2"] = False

if st.button("Deseja cadastrar um novo cliente ?"):
    st.session_state["button1"] = not st.session_state["button1"]

if st.session_state["button1"]:
    disco = st.text_input("Nome do Cliente: ", value="")
    if st.button("Salvar"):
        cursor.execute(sql, (id_v1, disco, today))
        st.success("O cliente foi adicionado ao banco de dados")
        con.commit()
        # st.session_state["df_cliente"] = pd.DataFrame(
        #     dta.data[dta.data["Nome do Cliente"] == disco]
        # )
        # nav_page("cliente_ativo")
        st._rerun()

st.markdown(
    """<hr style="height:1px;border:none;color:#9966ff;background-color:#9966ff;" /> """,
    unsafe_allow_html=True,
)

botao1, botao2 = st.columns(2)

with botao1:
    if st.button("Ver Portifolio"):
        st.session_state["df_cliente"] = pd.DataFrame(dta["selected_rows"])
        if st.session_state["df_cliente"].empty:
            st.error("Não foi selecionado um Cliente")
        else:
            nav_page("cliente_ativo")

with botao2:
    if st.button("Deletar um Cliente"):
        st.session_state["df_cliente"] = pd.DataFrame(dta["selected_rows"])
        if st.session_state["df_cliente"].empty:
            st.error("Não foi selecionado um Cliente")
        else:
            v2_client = int(st.session_state.df_cliente.client_id[0])
            cursor.execute("DELETE FROM cliente WHERE client_id = ?", (v2_client,))
            con.commit()
            st.success("O cliente foi deletado com sucesso")
            tm.sleep(1)
            st._rerun()


no_sidebar_style = """
    <style>
        div[data-testid="stSidebarNav"] {display: none;}
        footer {visibility: hidden;}
    </style>
"""
# st.markdown(no_sidebar_style, unsafe_allow_html=True)
