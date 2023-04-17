import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
import datetime as DT
import math
import time as tm
from func.redirect import nav_page
from st_aggrid import JsCode, AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
from st_aggrid.shared import GridUpdateMode, AgGridTheme
from database import con, cursor, base_df, besmart_base, moeda
import locale

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

st.set_page_config(
    page_icon="invest_smart_logo.png",
    page_title="Simulador - Clientes 0.25",
    initial_sidebar_state="collapsed",
    layout="wide",
)
# from func.connect import con, cursor


df = pd.read_sql("SELECT * FROM cliente", con)

dark = df.copy()
dark = dark.rename(
    columns={
        "nome_client": "Nome do Cliente",
        "data_cliente": "Data de Cadastro",
    }
)
id_v1 = st.session_state.usuario


dark = dark[dark["sigla"] == id_v1]

if dark.empty:
    dark = pd.DataFrame(
        columns={
            "client_id",
            "sigla",
            "Nome do Cliente",
            "Data de Cadastro",
            "Qnt. Ativos InvestSmart",
            "Qnt. Produtos BeSmart",
            "PL Aplicado",
        }
    ).fillna(0)

# st.dataframe(dark)
# dark[pl] = st.session_state.df_cliente.client_id[0]

col1, mid, col2 = st.columns([20, 2, 5])
with col1:
    st.write(
        fr'<p style="font-size:26px;">BEM VINDO AO SIMULADOR, {st.session_state.assessor}</p>',
        unsafe_allow_html=True,
    )

with col2:
    st.image("investsmart_endosso_horizontal_fundopreto.png", width=270)

st.markdown(
    """
    <hr style="height:1px;border:none;color:#9966ff;background-color:#9966ff;" /> 
    """,
    unsafe_allow_html=True,
)


#######################################################################################
############################ METRICS USADAS NOS BIGNUMBERS ############################
#######################################################################################

pl, ano1_avg, ano2_avg, retorno = st.columns([5, 5, 5, 3])
list_client_id = dark["client_id"].unique()
list_client_id = list(list_client_id)

fair = pd.read_sql("SELECT * FROM variaveis", con)

fair = fair[fair.client_id.isin(list_client_id)]
dicio = fair.groupby("client_id")["pl_aplicado"].sum()
dark["PL Aplicado"] = (
    df["client_id"]
    .map(dicio)
    .apply(lambda x: locale.currency(x, grouping=True, symbol=True))
)
dark["PL Aplicado"] = dark["PL Aplicado"].replace("R$ nan", "R$ 0")

fair["karma"] = [
    "InvestSmart" if x == "INVESTSMART" else "BeSmart" for x in fair["empresa"]
]
pl.metric(
    "PL Aplicado",
    "R$ " + locale.currency(fair.pl_aplicado.sum(), grouping=True, symbol=None),
)

if fair.pl_aplicado.sum() == 0:
    dark["Qnt. Ativos InvestSmart"] = 0
    dark["Qnt. Produtos BeSmart"] = 0
    dark["PL Aplicado"] = 0

else:
    dark["Qnt. Ativos InvestSmart"] = [
        fair[fair["client_id"] == x]
        .value_counts("karma", dropna=False)
        .reindex(fair.karma.unique(), fill_value=0)[0]
        if x in fair["client_id"].unique()
        else 0
        for x in dark["client_id"].unique()
    ]

    dark["Qnt. Produtos BeSmart"] = [
        fair[fair["client_id"] == x]
        .value_counts("karma", dropna=False)
        .reindex(fair.karma.unique(), fill_value=0)[1]
        if x in fair["client_id"].unique()
        else 0
        for x in dark["client_id"].unique()
    ]


smart = pd.DataFrame(columns=["Mês", "Resultado assessor"])
# st.dataframe(fair)

face = pd.read_excel("base_besmart_v2.xlsx")
face["Categoria"] = face["Categoria"].apply(lambda x: x.replace("_", " "))
face["Produto"] = face["Produto"].apply(lambda x: x.replace("_", " "))
face["porcem_repasse"] = face["porcem_repasse"] * 100.0

for i in fair["ativo_id"].unique():
    df = fair[fair["ativo_id"] == i]
    df = df.reset_index().drop("index", 1)

    # st.dataframe(df)
    if df.empresa.iloc[0] == "INVESTSMART":
        grasph_df = base_df(
            df.data_venc.iloc[0],
            df.data_ativo.iloc[0],
            df.pl_aplicado.iloc[0],
            df.retorno.iloc[0],
            df.roa_head.iloc[0],
            df.roa_rec.iloc[0],
            df.repasse.iloc[0],
            moeda_real=False,
        )
    else:

        grasph_df = besmart_base(
            df.data_venc.iloc[0],
            df.data_ativo.iloc[0],
            face,
            df.empresa.iloc[0],
            df.categoria.iloc[0],
            df.ativo.iloc[0],
            df.pl_aplicado.iloc[0],
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
result_month = final["Resultado assessor"][final["mes"] == DT.datetime.now().month]
avrg_year1 = final["Resultado assessor"][final["ano"] == DT.datetime.now().year].mean()
avrg_year2 = final["Resultado assessor"][
    final["ano"] == DT.datetime.now().year + 1
].mean()
try:
    retorno.metric(
        "Retorno Esperado para esse mês",
        "R$ "
        + locale.currency(
            result_month.iloc[0],
            grouping=True,
            symbol=None,
        ),
    )
except:
    retorno.metric(
        "Retorno Esperado para esse mês",
        "R$ "
        + locale.currency(
            0,
            grouping=True,
            symbol=None,
        ),
    )

ano1_avg.metric(
    f"Retorno Médio Esperado {DT.datetime.now().year}",
    "R$ "
    + locale.currency(
        avrg_year1,
        grouping=True,
        symbol=None,
    ),
)

ano2_avg.metric(
    f"Retorno Médio Esperado ano {DT.datetime.now().year+1}",
    "R$ "
    + locale.currency(
        avrg_year2,
        grouping=True,
        symbol=None,
    ),
)

#######################################################################################
############################### TABLES CLIENTE E ATIVOS ###############################
#######################################################################################

vazio1, cliente, vazio2 = st.columns([2, 7, 2])
with cliente:
    # dark["PL Aplicado"] = dark["PL Aplicado"].apply(lambda x: "R$ " + str(x))
    htmlstr = f"<p style='background-color: #9966ff; color: #000000; font-size: 16px; border-radius: 7px; padding-left: 8px; text-align: center'>Tabela de Clientes</style></p>"
    st.markdown(htmlstr, unsafe_allow_html=True)

    gridOptions = GridOptionsBuilder.from_dataframe(
        dark[
            [
                "Nome do Cliente",
                "Data de Cadastro",
                "PL Aplicado",
                "Qnt. Ativos InvestSmart",
                "Qnt. Produtos BeSmart",
            ]
        ]
    )

    gridOptions.configure_selection(
        selection_mode="single", use_checkbox=True, pre_selected_rows=[0]
    )
    gb = gridOptions.build()

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

st.session_state["df_cliente"] = pd.DataFrame(dta["selected_rows"])
if st.session_state["df_cliente"].empty:
    table2 = fair.copy()
else:
    table2 = fair[fair["client_id"] == st.session_state["df_cliente"].client_id.iloc[0]]


table2 = table2.rename(
    columns={
        "categoria": "Categoria",
        "ativo": "Ativo",
        "pl_aplicado": "PL Aplicado",
        "data_venc": "Data de Vencimento",
        "data_ativo": "Data de Início",
        "empresa": "Empresa",
    }
)

# with ativo:
#     htmlstr = f"<p style='background-color: #9966ff; color: #000000; font-size: 16px; border-radius: 7px; padding-left: 8px; text-align: center'>Tabela de Ativos</style></p>"
#     st.markdown(htmlstr, unsafe_allow_html=True)

#     gridOptions = GridOptionsBuilder.from_dataframe(
#         table2[
#             [
#                 # "client_id",
#                 "Empresa",
#                 "Categoria",
#                 "Ativo",
#                 "PL Aplicado",
#                 "Data de Início",
#                 "Data de Vencimento",
#                 # "shelf_id",
#             ]
#         ]
#     )

#     gridOptions.configure_selection(
#         selection_mode="single", use_checkbox=True, pre_selected_rows=[0]
#     )

#     gb = gridOptions.build()

#     dta_2 = AgGrid(
#         table2,
#         gridOptions=gb,
#         height=300,
#         allow_unsafe_jscode=True,
#         theme=AgGridTheme.ALPINE,
#         update_mode=GridUpdateMode.SELECTION_CHANGED,
#         columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW,
#         reload_data=True,
#     )

sql = "INSERT INTO cliente (sigla, nome_client, data_cliente) VALUES (?, ?, ?)"
today = DT.datetime.strftime(DT.datetime.today(), "%Y-%m-%d")
hoje = today


vacuo, botao_1, botao_2, botao_3, vacuo_2 = st.columns([7, 5, 5.5, 5, 7])
with botao_1:
    if "button1" not in st.session_state:
        st.session_state["button1"] = False

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

with botao_3:
    if "button42" not in st.session_state:
        st.session_state["button42"] = False

    if st.button("Deletar o Cliente Selecionado"):
        st.session_state["button42"] = not st.session_state["button42"]

    if st.session_state["button42"]:
        disco = st.write("Tem Certeza ?")
        sim, nao = st.columns(2)
        with sim:
            if st.button("Sim"):
                if (
                    st.session_state["df_cliente"].empty
                    or dta.data["Data de Cadastro"].iloc[0] == "None"
                ):
                    st.error("Não foi selecionado um Cliente")
                else:
                    v2_client = int(st.session_state.df_cliente.client_id[0])
                    cursor.execute(
                        "DELETE FROM cliente WHERE client_id = ?", (v2_client,)
                    )
                    con.commit()
                    st.success("O cliente foi deletado com sucesso")
                    tm.sleep(1)
                    st._rerun()
        with nao:
            if st.button("Não"):
                st.session_state["button42"] = False

with botao_2:
    if st.button("Abrir o Portifolio do Cliente Selecionado"):
        if (
            st.session_state["df_cliente"].empty
            or dta.data["Data de Cadastro"].iloc[0] == "None"
        ):
            st.error("Não foi selecionado um Cliente")
        else:
            nav_page("cliente_wide")


#######################################################################################
################################### GRAFICOS FEITOS ###################################
#######################################################################################

st.markdown(
    """
    <hr style="height:1px;border:none;color:#9966ff;background-color:#9966ff;" /> 
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
        div[data-testid="stSidebarNav"] {display: none;}
        footer {visibility: hidden;}
        
        [data-testid="collapsedControl"] {display: none}
        footer {visibility: hidden;}
        
        div[data-testid="stSidebarNav"] {display: none;}
        footer {visibility: hidden;}

        img{
        background-color: rgb(14, 17, 23);
            }
        
    </style>
""",
    unsafe_allow_html=True,
)

chart1, chart2 = st.columns([6, 4])
with chart2:
    try:
        st.text("")
        st.text("")
        st.text("")
        st.text("")
        df_categ = fair.groupby("categoria")["pl_aplicado"].sum().reset_index()
        # st.dataframe(df_categ)
        fig = px.bar(
            df_categ.sort_values(by="pl_aplicado", ascending=False),
            x="pl_aplicado",
            y="categoria",
            width=700,
            # height=500,
            text="R$ "
            + round(df_categ.pl_aplicado.sort_values(ascending=False), 2).astype(str),
            color="categoria",
            color_discrete_sequence=px.colors.sequential.Viridis,
            title="Pl aplicado por Categoria, todos clientes",
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
        fig.update_yaxes(showgrid=False)
        fig.update_xaxes(showgrid=False)
        fig.data[0].marker.color = "#9966ff"
        fig.data[0].textfont.color = "white"
        fig.data[0].textposition = "auto"
        fig.data[0].insidetextanchor = "middle"
        st.plotly_chart(fig)
    except:
        st.error("Você não possui um Portifolio nesta ferramenta")
with chart1:
    if final.empty:
        st.text("")
        st.text("")
        st.text("")
        st.text("")
        st.error("Você não possui um Portifolio nesta ferramenta")
    else:
        tab1, tab2 = st.tabs(["Grafico Geral", "Grafico Geral por Cliente"])
        with tab1:
            fig = px.line(
                final,
                x="Mês",
                y="Resultado assessor",
                markers=True,
                width=1000,
                text="R$ " + round(final["Resultado assessor"], 2).astype(str),
                title=f"Resultado Geral do Assessor por mês",
            )
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(title_font_size=24, griddash="dot", rangemode="tozero")
            fig.update_traces(textposition="top center")
            fig.data[0].line.color = "#9966ff"
            st.plotly_chart(fig)
        # st.dataframe(st.session_state["df_cliente"])
        with tab2:
            try:
                if (
                    st.session_state["df_cliente"]["Qnt. Ativos InvestSmart"].iloc[0]
                    + st.session_state["df_cliente"]["Qnt. Produtos BeSmart"].iloc[0]
                    == 0
                ):
                    st.error("Esse Cliente não tem Portifolio")
                else:
                    if not st.session_state["df_cliente"].empty:
                        fair = fair[
                            fair["client_id"]
                            == st.session_state["df_cliente"].client_id.iloc[0]
                        ]
                        smart_v2 = pd.DataFrame()
                        for i in fair["ativo_id"].unique():
                            df = fair[fair["ativo_id"] == i]
                            df = df.reset_index().drop("index", 1)

                            # st.dataframe(df)
                            if df.empresa.iloc[0] == "INVESTSMART":
                                grasph_df = base_df(
                                    df.data_venc.iloc[0],
                                    df.data_ativo.iloc[0],
                                    df.pl_aplicado.iloc[0],
                                    df.retorno.iloc[0],
                                    df.roa_head.iloc[0],
                                    df.roa_rec.iloc[0],
                                    df.repasse.iloc[0],
                                    moeda_real=False,
                                )
                            else:
                                grasph_df = besmart_base(
                                    df.data_venc.iloc[0],
                                    df.data_ativo.iloc[0],
                                    face,
                                    df.empresa.iloc[0],
                                    df.categoria.iloc[0],
                                    df.ativo.iloc[0],
                                    df.pl_aplicado.iloc[0],
                                    df.repasse.iloc[0],
                                )
                            smart_v2 = smart_v2.append(grasph_df)
                        smart_v2["Mês"] = smart_v2["Mês"].apply(
                            lambda x: DT.datetime.strptime(x, "%b-%y")
                        )
                        smart_v2["Mês"] = smart_v2["Mês"].apply(
                            lambda x: DT.datetime.strftime(x, "%m-%y")
                        )
                        # st.dataframe(smart_v2)
                        final_v2 = (
                            smart_v2[["Mês", "Resultado assessor"]]
                            .groupby(smart_v2["Mês"])["Resultado assessor"]
                            .sum()
                            .reset_index()
                        )
                        final_v2["Mês"] = final_v2["Mês"].apply(
                            lambda x: DT.datetime.strptime(x, "%m-%y")
                        )
                        final_v2["ano"] = final_v2["Mês"].astype("datetime64").dt.year
                        final_v2["mes"] = final_v2["Mês"].astype("datetime64").dt.month
                        final_v2["Mês"] = final_v2["Mês"].apply(
                            lambda x: DT.datetime.strftime(x, "%b-%y")
                        )
                        final_v2 = final_v2.sort_values(["ano", "mes"]).reset_index(
                            drop=True
                        )
                        name_v2 = st.session_state.df_cliente["Nome do Cliente"][0]
                        fig = px.line(
                            final_v2,
                            x="Mês",
                            y="Resultado assessor",
                            width=1000,
                            markers=True,
                            text="R$ "
                            + round(final_v2["Resultado assessor"], 2).astype(str),
                            title=f"Resultado Geral do Assessor por mês de {name_v2}",
                        )
                        fig.update_xaxes(showgrid=False)
                        fig.update_yaxes(
                            title_font_size=24, griddash="dot", rangemode="tozero"
                        )
                        fig.update_traces(textposition="top center")
                        fig.data[0].line.color = "#9966ff"
                        st.plotly_chart(fig)
            except:
                fig = px.line(
                    final,
                    x="Mês",
                    y="Resultado assessor",
                    width=1000,
                    markers=True,
                    text="R$ " + round(final["Resultado assessor"], 2).astype(str),
                    title=f"Resultado Geral do Assessor por mês",
                )
                fig.update_xaxes(showgrid=False)
                fig.update_yaxes(title_font_size=24, griddash="dot", rangemode="tozero")
                fig.update_traces(textposition="top center")
                fig.data[0].line.color = "#9966ff"
                st.plotly_chart(fig)
