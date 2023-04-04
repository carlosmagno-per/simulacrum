import streamlit as st
import plotly.express as px
import numpy as np
import pandas as pd
import datetime as DT
import math
import time as tm
from func.redirect import nav_page
from st_aggrid import JsCode, AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
from st_aggrid.shared import GridUpdateMode, AgGridTheme
from database import con, cursor, base_df, besmart_base

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
        "data_ativo": "Data de Início",
        "empresa": "Empresa",
    }
)

dark = dark[dark["client_id"] == v3]

st.set_page_config(
    page_icon="invest_smart_logo.png",
    page_title="Simulador - Ativos 0.15",
    initial_sidebar_state="collapsed",
    # layout="wide",
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
            "Empresa",
            "Categoria",
            "Ativo",
            "PL Aplicado",
            "Data de Início",
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
        # width=5000,
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

# st.dataframe(st.session_state.df_ativo)

if "button1" not in st.session_state:
    st.session_state["button1"] = False

botao1, botao2 = st.columns(2)

with botao1:
    if st.button("Incluir um novo ativo InvestSmart"):
        nav_page("novo_ativo")

with botao2:
    if st.button("Incluir um novo ativo Be.Smart"):
        #         st.session_state["button1"] = not st.session_state["button1"]
        # if st.session_state["button1"]:
        # checks = st.radio(
        #     "Qual tipo de produto será Incluido:",
        #     [
        #         "Cambio",
        #         "Protect",
        #         "Credito",
        #         "Diversificações",
        #         "Empresas",
        #     ],
        #     horizontal=True,
        # )
        # if st.button("Incluir esse tipo de ativo"):
        nav_page("besmart_novo_ativo")

st.markdown(
    """
    <hr style="height:1px;border:none;color:#9966ff;background-color:#9966ff;" /> 
    <p > Gráfico com visao da Comissão do Assessor</p>
    """,
    unsafe_allow_html=True,
)

if "button10" not in st.session_state:
    st.session_state["button10"] = False

face = pd.read_excel("base_besmart.xlsx")
face["Categoria"] = face["Categoria"].apply(lambda x: x.replace("_", " "))
face["Produto"] = face["Produto"].apply(lambda x: x.replace("_", " "))
face["porcem_repasse"] = face["porcem_repasse"] * 100.0

if st.button("Ver o Gráfico, Ganho do Assessor"):
    st.session_state["button10"] = not st.session_state["button10"]
if st.session_state["button10"]:
    tab1, tab2 = st.tabs(["Grafico cliente selecionado", "Grafico Geral"])
    with tab1:
        if st.session_state["df_ativo"].empty:
            st.error(
                "Não há como mostrar um gráfico, pois não foi selecionado um ativo"
            )
        else:
            if st.session_state.df_ativo.Empresa.iloc[0] == "INVESTSMART":
                grasph_df = base_df(
                    st.session_state.df_ativo["Data de Vencimento"].iloc[0],
                    st.session_state.df_ativo["Data de Início"].iloc[0],
                    st.session_state.df_ativo["PL Aplicado"].iloc[0],
                    st.session_state.df_ativo.retorno.iloc[0],
                    st.session_state.df_ativo.roa_head.iloc[0],
                    st.session_state.df_ativo.roa_rec.iloc[0],
                    st.session_state.df_ativo.repasse.iloc[0],
                    moeda_real=False,
                )
            else:
                grasph_df = besmart_base(
                    st.session_state.df_ativo["Data de Vencimento"].iloc[0],
                    st.session_state.df_ativo["Data de Início"].iloc[0],
                    face,
                    st.session_state.df_ativo.Empresa.iloc[0],
                    st.session_state.df_ativo.Categoria.iloc[0],
                    st.session_state.df_ativo.Ativo.iloc[0],
                    st.session_state.df_ativo["PL Aplicado"].iloc[0],
                    st.session_state.df_ativo.repasse.iloc[0],
                )
            # st.dataframe(grasph_df)
            fig = px.line(
                grasph_df,
                x="Mês",
                y="Resultado assessor",
                markers=True,
                text="R$ " + round(grasph_df["Resultado assessor"], 2).astype(str),
                title=f"""Categoria: {dark.Categoria.iloc[0]}\n
                Ativo: {dark.Ativo.iloc[0]}\n 
                Cliente: {name_v1}""",
            )
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(title_font_size=24, griddash="dot", rangemode="tozero")
            fig.data[0].line.color = "#9966ff"
            st.plotly_chart(fig)
    with tab2:
        smart = pd.DataFrame(columns=["Mês", "Resultado assessor"])
        for i in dark["ativo_id"].unique():
            df = dark[dark["ativo_id"] == i]
            df = df.reset_index().drop("index", 1)

            # st.dataframe(df)
            if df.Empresa.iloc[0] == "INVESTSMART":
                grasph_df = base_df(
                    df["Data de Vencimento"].iloc[0],
                    df["Data de Início"].iloc[0],
                    df["PL Aplicado"].iloc[0],
                    df.retorno.iloc[0],
                    df.roa_head.iloc[0],
                    df.roa_rec.iloc[0],
                    df.repasse.iloc[0],
                    moeda_real=False,
                )
            else:

                grasph_df = besmart_base(
                    df["Data de Vencimento"].iloc[0],
                    df["Data de Início"].iloc[0],
                    face,
                    df.Empresa.iloc[0],
                    df.Categoria.iloc[0],
                    df.Ativo.iloc[0],
                    df["PL Aplicado"].iloc[0],
                    df.repasse.iloc[0],
                )
            # st.dataframe(grasph_df)
            smart = smart.append(grasph_df)
        smart["Mês"] = smart["Mês"].apply(lambda x: DT.datetime.strptime(x, "%b-%y"))
        smart["Mês"] = smart["Mês"].apply(lambda x: DT.datetime.strftime(x, "%m-%y"))
        # st.dataframe(smart)
        final = (
            smart[["Mês", "Resultado assessor"]]
            .groupby(smart["Mês"])["Resultado assessor"]
            .sum()
            .reset_index()
        )
        final["Mês"] = final["Mês"].apply(lambda x: DT.datetime.strptime(x, "%m-%y"))
        final["ano"] = final["Mês"].astype("datetime64").dt.year
        final["mes"] = final["Mês"].astype("datetime64").dt.month
        final["Mês"] = final["Mês"].apply(lambda x: DT.datetime.strftime(x, "%b-%y"))
        final = final.sort_values(["ano", "mes"]).reset_index(drop=True)
        # st.dataframe(final)
        fig = px.line(
            final,
            x="Mês",
            y="Resultado assessor",
            markers=True,
            text="R$ " + round(final["Resultado assessor"], 2).astype(str),
            title=f"Resultado Geral do Assessor por mês",
        )
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(title_font_size=24, griddash="dot", rangemode="tozero")
        fig.data[0].line.color = "#9966ff"
        st.plotly_chart(fig)


st.markdown(
    """<hr style="height:1px;border:none;color:#9966ff;background-color:#9966ff;" /> """,
    unsafe_allow_html=True,
)


botao3, botao4, botao5 = st.columns(3)
with botao3:
    if st.button("Voltar"):
        nav_page("assessor_cliente")

with botao4:
    if st.button("Editar o Ativo Selecionado"):
        if st.session_state["df_ativo"].empty:
            st.error("Não foi selecionado um ativo")
        else:
            if st.session_state.df_ativo.Empresa.iloc[0] == "INVESTSMART":
                nav_page("edit_ativo")
            else:
                nav_page("besmart_edit_ativo")


with botao5:
    if st.button("Deletar o Ativo Selecionado"):
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
    img{
    background-color: rgb(14, 17, 23);
}
</style>
""",
    unsafe_allow_html=True,
)
