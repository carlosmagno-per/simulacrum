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
import locale

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
# from func.connect import con, cursor


df = pd.read_sql("SELECT * FROM variaveis", con)

v3 = st.session_state.df_cliente.client_id[0]

name_v1 = st.session_state.df_cliente["Nome do Cliente"][0]
dt_cads = st.session_state.df_cliente["Data de Cadastro"][0]

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

df_ativo = dark.copy()

st.set_page_config(
    page_icon="invest_smart_logo.png",
    page_title="Simulador - Ativos 0.25",
    initial_sidebar_state="collapsed",
    layout="wide",
)


col1, mid, col2 = st.columns([12, 8, 5])
with col1:
    st.write(
        fr'<p style="font-size:30px;">Ativos do Cliente: {name_v1}</p>',
        unsafe_allow_html=True,
    )
    st.write(
        fr'<p style="font-size:30px;">Data de Cadastro: {dt_cads}</p>',
        unsafe_allow_html=True,
    )
    if st.button("Voltar a visão Geral"):
        nav_page("wide_project")
with col2:
    st.image("investsmart_endosso_horizontal_fundopreto.png", width=270)

with mid:
    st.write(fr'<p style="font-size:30px;">Portifólios</p>',
        unsafe_allow_html=True,)
st.markdown(
    """
    <hr style="height:1px;border:none;color:#9966ff;background-color:#9966ff;" /> 
    """,
    unsafe_allow_html=True,
)

pl, retorno, ano1_avg, ano2_avg = st.columns([5, 5, 5, 3])

chart1, chart2 = st.columns([6, 4])

st.markdown(
    """
    <hr style="height:1px;border:none;color:#9966ff;background-color:#9966ff;" /> 
    """,
    unsafe_allow_html=True,
)


# st.table(dark)
vacuo, botao1, botao2, botao3, botao4, vacuo2 = st.columns([7, 5, 5, 5, 5, 7])
font_css = """
<style>
button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
  font-size: 24px;
}
</style>
"""
st.write(font_css, unsafe_allow_html=True)

tab1, tab2 = st.tabs(["InvestSmart", "Be.Smart"])

with tab1:
    vazio1, cliente, vazio2 = st.columns([1, 9, 1])
    dark["PL Aplicado"] = dark["PL Aplicado"].apply(
        lambda x: locale.currency(x, grouping=True, symbol=True)
    )
    with cliente:
        dark2 = dark[dark["Empresa"]=="INVESTSMART"]
        gridOptions = GridOptionsBuilder.from_dataframe(
            dark2[
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
            htmlstr = f"<p style='background-color: #9966ff; color: #000000; font-size: 16px; border-radius: 7px; padding-left: 8px; text-align: center'>Tabela de Produtos</style></p>"
            st.markdown(htmlstr, unsafe_allow_html=True)

            dta = AgGrid(
                dark2,
                gridOptions=gb,
                #height=290,
                # width=5000,
                allow_unsafe_jscode=True,
                theme=AgGridTheme.ALPINE,
                update_mode=GridUpdateMode.SELECTION_CHANGED,
                columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW,
                reload_data=True,
                key="investsnart"
            )
with tab2:
    vazio1, cliente, vazio2 = st.columns([1, 9, 1])
    with cliente:
        dark3 = dark[dark["Empresa"]!="INVESTSMART"]
        gridOptions = GridOptionsBuilder.from_dataframe(
            dark3[
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
            htmlstr = f"<p style='background-color: #9966ff; color: #000000; font-size: 16px; border-radius: 7px; padding-left: 8px; text-align: center'>Tabela de Produtos</style></p>"
            st.markdown(htmlstr, unsafe_allow_html=True)

            dta = AgGrid(
                dark3,
                gridOptions=gb,
                #height=290,
                # width=5000,
                allow_unsafe_jscode=True,
                theme=AgGridTheme.ALPINE,
                update_mode=GridUpdateMode.SELECTION_CHANGED,
                columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW,
                reload_data=True,
            )

st.session_state["df_ativo"] = pd.DataFrame(dta["selected_rows"])

# st.dataframe(st.session_state.df_ativo)


if "button1" not in st.session_state:
    st.session_state["button1"] = False
with botao1:
    if st.button("Incluir Ativo InvestSmart"):
        nav_page("novo_ativo")
with botao2:
    if st.button("Incluir Serviço Be.Smart"):
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
with botao3:
    if st.button("Visualizar o Ativo Selecionado"):
        if st.session_state["df_ativo"].empty:
            st.error("Não foi selecionado um ativo")
        else:
            if st.session_state.df_ativo.Empresa.iloc[0] == "INVESTSMART":
                nav_page("edit_ativo")
            else:
                nav_page("besmart_edit_ativo")
with botao4:
    if "button44" not in st.session_state:
        st.session_state["button44"] = False
    if st.button("Deletar o Ativo Selecionado"):
        st.session_state["button44"] = not st.session_state["button44"]

    if st.session_state["button44"]:
        disco = st.write("Tem Certeza ?")
        sim, nao = st.columns(2)
        with sim:
            if st.button("Sim"):
                if st.session_state["df_ativo"].empty:
                    st.error("Não foi selecionado um Cliente")
                else:
                    vers = int(st.session_state.df_ativo.ativo_id[0])
                    cursor.execute("DELETE FROM variaveis WHERE ativo_id = ?", (vers,))
                    con.commit()
                    st.success("O ativo foi deletado com sucesso")
                    tm.sleep(1)
                    st._rerun()
        with nao:
            if st.button("Não"):
                st.session_state["button44"] = False
        # if st.session_state["df_ativo"].empty:
        #     st.error("Não foi selecionado um ativo")
        # else:
        #



face = pd.read_excel("base_besmart_v2.xlsx")
face["Categoria"] = face["Categoria"].apply(lambda x: x.replace("_", " "))
face["Produto"] = face["Produto"].apply(lambda x: x.replace("_", " "))
face["porcem_repasse"] = face["porcem_repasse"] * 100.0

with chart1:
    if (
        st.session_state["df_cliente"]["Qnt. Ativos InvestSmart"].iloc[0]
        + st.session_state["df_cliente"]["Qnt. Produtos BeSmart"].iloc[0]
        == 0
    ):

        st.text("")
        st.error("Esse Cliente não tem Portifólio")
    else:
        # tab1, tab2 = st.tabs(["Grafico Geral", "Grafico por Ativo Selecionado"])
        # with tab2:
        #     if st.session_state["df_ativo"].empty:

        #         st.text("")
        #         st.error(
        #             "Não há como mostrar um gráfico, pois não foi selecionado um ativo"
        #         )
        #     else:
        #         if st.session_state.df_ativo.Empresa.iloc[0] == "INVESTSMART":
        #             grasph_df = base_df(
        #                 st.session_state.df_ativo["Data de Vencimento"].iloc[0],
        #                 st.session_state.df_ativo["Data de Início"].iloc[0],
        #                 float(
        #                     st.session_state.df_ativo["PL Aplicado"]
        #                     .iloc[0][3:]
        #                     .replace(".", "")
        #                     .replace(",", ".")
        #                 ),
        #                 st.session_state.df_ativo.retorno.iloc[0],
        #                 st.session_state.df_ativo.roa_head.iloc[0],
        #                 st.session_state.df_ativo.roa_rec.iloc[0],
        #                 st.session_state.df_ativo.repasse.iloc[0],
        #                 moeda_real=False,
        #             )
        #         else:
        #             grasph_df = besmart_base(
        #                 st.session_state.df_ativo["Data de Vencimento"].iloc[0],
        #                 st.session_state.df_ativo["Data de Início"].iloc[0],
        #                 face,
        #                 st.session_state.df_ativo.Empresa.iloc[0],
        #                 st.session_state.df_ativo.Categoria.iloc[0],
        #                 st.session_state.df_ativo.Ativo.iloc[0],
        #                 float(
        #                     st.session_state.df_ativo["PL Aplicado"]
        #                     .iloc[0][3:]
        #                     .replace(".", "")
        #                     .replace(",", ".")
        #                 ),
        #                 st.session_state.df_ativo.repasse.iloc[0],
        #             )
        #         # st.dataframe(grasph_df)
        #         fig = px.line(
        #             grasph_df,
        #             x="Mês",
        #             y="Resultado assessor",
        #             width=1000,
        #             markers=True,
        #             text="R$ " + round(grasph_df["Resultado assessor"], 2).astype(str),
        #             title=f"""Categoria: {st.session_state["df_ativo"].Categoria.iloc[0]}<br>Ativo: {st.session_state["df_ativo"].Ativo.iloc[0]}""",  # <br>Cliente: {name_v1}""",
        #         )
        #         fig.update_traces(textposition="top center")
        #         fig.update_xaxes(showgrid=False)
        #         fig.update_yaxes(title_font_size=24, griddash="dot", rangemode="tozero")
        #         fig.data[0].line.color = "#9966ff"
        #         st.plotly_chart(fig)
        # with tab1:
        smart = pd.DataFrame(columns=["Mês", "Resultado assessor"])
        for i in dark["ativo_id"].unique():
            df_v2 = dark[dark["ativo_id"] == i]
            df_v2 = df_v2.reset_index().drop("index", 1)

            #st.dataframe(df_v2)
            if df_v2.Empresa.iloc[0] == "INVESTSMART":
                grasph_df = base_df(
                    df_v2["Data de Vencimento"].iloc[0],
                    df_v2["Data de Início"].iloc[0],
                    float(
                        df_v2["PL Aplicado"]
                        .iloc[0][3:]
                        .replace(".", "")
                        .replace(",", ".")
                    ),
                    df_v2.retorno.iloc[0],
                    df_v2.roa_head.iloc[0],
                    df_v2.roa_rec.iloc[0],
                    df_v2.repasse.iloc[0],
                    moeda_real=False,
                )
                grasph_df["ativo_id"] = i
            else:

                grasph_df = besmart_base(
                    df_v2["Data de Vencimento"].iloc[0],
                    df_v2["Data de Início"].iloc[0],
                    face,
                    df_v2.Empresa.iloc[0],
                    df_v2.Categoria.iloc[0],
                    df_v2.Ativo.iloc[0],
                    float(
                        df_v2["PL Aplicado"]
                        .iloc[0][3:]
                        .replace(".", "")
                        .replace(",", ".")
                    ),
                    df_v2.repasse.iloc[0],
                )
                grasph_df["ativo_id"] = i
            # st.dataframe(grasph_df)
            smart = smart.append(grasph_df)
            
        smart["Mês"] = smart["Mês"].apply(
            lambda x: DT.datetime.strptime(x, "%b-%y")
        )
        smart["Mês"] = smart["Mês"].apply(
            lambda x: DT.datetime.strftime(x, "%m-%y")
        )
        mapas = dict(dark[["ativo_id","Ativo"]].values)
        smart["Produtos"] = smart.ativo_id.map(mapas)
        #st.dataframe(smart)
        
        
        final = (
            smart[["Mês", "Resultado assessor","Produtos"]]
            .groupby(["Mês","Produtos"]).sum()
            .reset_index()
        )
        
        #st.dataframe(final)
        
        final["Mês"] = final["Mês"].apply(
            lambda x: DT.datetime.strptime(x, "%m-%y")
        )
        final["ano"] = final["Mês"].astype("datetime64").dt.year
        final["mes"] = final["Mês"].astype("datetime64").dt.month
        final["Mês"] = final["Mês"].apply(
            lambda x: DT.datetime.strftime(x, "%b-%y")
        )
        final = final.sort_values(["ano", "mes"]).reset_index(drop=True)
        #st.dataframe(final)
        fig = px.bar(
            final,
            x="Mês",
            y="Resultado assessor",
            color="Produtos",
            width=1000,
            height=425,
            text_auto='.2s',
            title=f"Comissão Total Mensal",
            color_discrete_sequence=px.colors.sequential.Viridis,
            labels = {"Resultado assessor":"Comissão do Assessor (R$)"}
        )
        fig.update_layout(
            #showlegend=False,
            legend_title= None,
            uniformtext_minsize=8,
            uniformtext_mode="hide",
            legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
            )
            )
        fig.update_traces(textfont_size=25)
        fig.data[0].textfont.color = "white"
        fig.data[0].marker.color = "#9966ff"
        fig.data[1].marker.color = "#482878"
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(title=None)
        #fig.update_traces(textposition="top center")
        st.plotly_chart(fig)
with chart2:
    if (
        st.session_state["df_cliente"]["Qnt. Ativos InvestSmart"].iloc[0]
        + st.session_state["df_cliente"]["Qnt. Produtos BeSmart"].iloc[0]
        == 0
    ):

        st.text("")
        st.error("Esse Cliente não tem Portifólio")
    else:
        # try:
        # st.dataframe(dark)
        # st.dataframe(df_ativo)
        df_categ = df_ativo.groupby("Ativo")["PL Aplicado"].sum().reset_index()
        df_categ["Valor"] = df_categ["PL Aplicado"].astype(str).apply( lambda x: x[:-2])
        #st.dataframe(df_categ)
        fig = px.bar(
            df_categ.sort_values(by="PL Aplicado", ascending=False),
            x="PL Aplicado",
            y="Ativo",
            width=700,
            # height=500,
            text="R$ "
            + df_categ["Valor"].sort_values(ascending=False).astype(
                str
            ),
            color="Ativo",
            color_discrete_sequence=px.colors.sequential.Viridis,
            title="Pl aplicado por Ativos, todos clientes",
        )
        fig.update_layout(
            font=dict(family="Arial", size=18, color="White"),
            # paper_bgcolor="rgba(0,0,0,0)",
            # plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(title="", tickvals=[], ticktext=[]),
            yaxis=dict(title=""),
            showlegend=False,
            uniformtext_minsize=8,
            uniformtext_mode="hide",
        )
        fig.update_traces(textposition='auto',insidetextanchor = "middle")
        fig.update_yaxes(showgrid=False)
        fig.update_xaxes(showgrid=False)
        fig.data[0].marker.color = "#9966ff"
        fig.data[0].textfont.color = "white"
        st.plotly_chart(fig)
        # except:
        #     st.error("Você não possui um Portifolio nesta ferramenta")

st.markdown(
    """<hr style="height:1px;border:none;color:#9966ff;background-color:#9966ff;" /> """,
    unsafe_allow_html=True,
)

pl.metric(
    "Total do Portifólio",
    "R$ " + locale.currency(df_ativo["PL Aplicado"].sum(), grouping=True, symbol=None)[:-3],
)
    

try:
    result_month = final["Resultado assessor"][(final["mes"] == DT.datetime.now().month)& (final["ano"] == DT.datetime.now().year)].sum()

    avrg_year1 = (final["Resultado assessor"][
        final["ano"] == DT.datetime.now().year
    ].sum())
    avrg_year2 = (final["Resultado assessor"][
        final["ano"] == DT.datetime.now().year + 1
    ].sum())
except:
    result_month = 0
    avrg_year1 = 0
    avrg_year2 = 0
try:
    retorno.metric(
        "Comissão Esperada para esse mês",
        "R$ "
        + locale.currency(
            result_month,
            grouping=True,
            symbol=None,
        )[:-3],
    )
except:
    retorno.metric(
        "Comissão Esperada para esse mês",
        "R$ "
        + locale.currency(
            0,
            grouping=True,
            symbol=None,
        )[:-3],
    )

ano1_avg.metric(
    f"Comissão Esperada {DT.datetime.now().year}",
    "R$ "
    + locale.currency(
        avrg_year1,
        grouping=True,
        symbol=None,
    )[:-3],
)

if np.isnan(avrg_year2):
    ano2_avg.metric(
        f"Comissão Esperada {DT.datetime.now().year+1}",
        "R$ "
        + locale.currency(
            0,
            grouping=True,
            symbol=None,
        )[:-3],
    )
else:
    ano2_avg.metric(
        f"Comissão Esperada {DT.datetime.now().year+1}",
        "R$ "
        + locale.currency(
            avrg_year2,
            grouping=True,
            symbol=None,
        )[:-3],
    )


if st.button("Voltar"):
    nav_page("wide_project")

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
