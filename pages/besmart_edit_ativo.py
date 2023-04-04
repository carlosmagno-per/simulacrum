import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import datetime as DT
import math
import numpy
import time as tm
from func.redirect import nav_page
import pymysql
from sqlalchemy import create_engine
from database import con, cursor, moeda, base_df
import locale

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

# from func.connect import con, cursor


st.set_page_config(
    page_icon="invest_smart_logo.png",
    page_title="Simulador - Edit Ativos 0.15",
    initial_sidebar_state="collapsed",
    # layout="wide",
)

col1, mid, col2 = st.columns([20, 1, 16])
with col1:
    st.empty()
with col2:
    st.image(
        "BeSmart_Logos_AF_horizontal__branco.png",
    )

st.header("Editando um Ativo")


v4 = int(st.session_state.df_ativo.ativo_id[0])

v1_empresa = st.session_state.df_ativo.Empresa.iloc[0]
v1_categ = st.session_state.df_ativo.Categoria.iloc[0]
v1_ativo = st.session_state.df_ativo.Ativo.iloc[0]
v1_data = st.session_state.df_ativo["Data de Vencimento"].iloc[0]
v1_data_inicio = st.session_state.df_ativo["Data de Início"].iloc[0]
v1_pl_apl = st.session_state.df_ativo["PL Aplicado"].iloc[0]
v1_retorno = st.session_state.df_ativo.retorno.iloc[0]
v1_repasse = st.session_state.df_ativo.repasse.iloc[0]
v1_roa_head = st.session_state.df_ativo.roa_head.iloc[0]
v1_roa_rec = st.session_state.df_ativo.roa_rec.iloc[0]

st.markdown(
    """<hr style="height:1px;border:none;color:#9966ff;background-color:#9966ff;" /> """,
    unsafe_allow_html=True,
)

st.subheader("**Premissas**")

face = pd.read_excel("base_besmart.xlsx")
face["Categoria"] = face["Categoria"].apply(lambda x: x.replace("_", " "))
face["Produto"] = face["Produto"].apply(lambda x: x.replace("_", " "))
face["porcem_repasse"] = face["porcem_repasse"] * 100.0
v3 = int(st.session_state.df_cliente.client_id[0])
name_v1 = st.session_state.df_cliente["Nome do Cliente"][0]

# st.write(v3)
# st.write(name_v1)

empresa_list = list(face.Empresa.unique())

colNome1, colValue1 = st.columns(2)

with colNome1:
    empresa = st.selectbox(
        "Empresa, Be.Smart: ", face.Empresa.unique(), empresa_list.index(v1_empresa)
    )

try:
    ind = list(face.Categoria[face["Empresas"] == empresa].unique()).index(v1_categ)
    with colValue1:
        categoria = st.selectbox(
            "Categoria: ",
            list(face.Categoria[face["Empresa"] == empresa].unique()),
            index=ind,
        )
except:
    with colValue1:
        categoria = st.selectbox(
            "Categoria: ", list(face.Categoria[face["Empresa"] == empresa].unique())
        )

colvalor, colpain = st.columns(2)
with colvalor:
    pl_apl = st.number_input(
        "Valor da Venda (R$): ",
        min_value=0.0,
        format="%f",
        value=float(v1_pl_apl),
        step=1000.0,
    )
    st.text("R$" + locale.currency(pl_apl, grouping=True, symbol=None))
try:
    ind_2 = list(face.Produto[face["Categoria"] == categoria].unique()).index(v1_ativo)
    with colpain:
        produto = st.selectbox(
            "Produto: ",
            list(face.Produto[face["Categoria"] == categoria].unique()),
            index=ind_2,
        )
except:
    with colpain:
        produto = st.selectbox(
            "Produto: ",
            list(face.Produto[face["Categoria"] == categoria].unique()),
        )


colNome3, colValue3 = st.columns(2)
with colNome3:
    data_inicial = st.date_input(
        "Data de Início: ",
        # min_value=DT.date.today()
        value=DT.datetime.strptime(v1_data_inicio[:10], "%Y-%m-%d"),
    )

with colValue3:
    data = st.date_input(
        "Data de Vencimento: ",
        # min_value=DT.date.today()
        value=DT.datetime.strptime(v1_data[:10], "%Y-%m-%d"),
    )

dias = DT.datetime.strptime(str(data), "%Y-%m-%d") - DT.datetime.strptime(
    str(data_inicial), "%Y-%m-%d"
)
mes = round(dias.days / 30)

if mes < 1:
    mes = 1
else:
    mes = mes

roa_reps = st.number_input(
    "Repasse Assessor (%): ",
    min_value=0.0,
    format="%f",
    value=float(v1_repasse),
    max_value=100.0,
    step=1.0,
)

# colcom_brt, colporrep = st.columns(2)
# with colcom_brt:


# with colporrep:
#     imposto = st.number_input(
#         "Comissão (%): ",
#         min_value=0.0,
#         format="%.2f",
#         value=20.0,
#         step=0.1,
#     )
st.markdown(
    """<hr style="height:1px;border:none;color:#9966ff;background-color:#9966ff;" /> 
    <p > Visualização do produto por uma tabela </p>
    """,
    unsafe_allow_html=True,
)


if data > data_inicial:

    dias = DT.datetime.strptime(str(data), "%Y-%m-%d") - DT.datetime.strptime(
        str(data_inicial), "%Y-%m-%d"
    )
    mes = round(dias.days / 30)

    endDate = DT.datetime.strptime(str(data), "%Y-%m-%d")
    startDate = DT.datetime.strptime(str(data_inicial), "%Y-%m-%d")

    # Getting List of Days using pandas
    if mes < 1:
        datesRange = pd.date_range(startDate, periods=1, freq="m")
        datesRange = list(datesRange)
    else:
        datesRange = pd.date_range(startDate, periods=mes + 1, freq="m")
        datesRange = list(datesRange)

    datesRange = [DT.datetime.strftime(x, "%b-%y") for x in datesRange]

    datesRange = pd.DataFrame(datesRange)

    df = pd.DataFrame()
    masquerede = face[
        (face["Empresa"] == empresa)
        & (face["Categoria"] == categoria)
        & (face["Produto"] == produto)
    ][["porcem_repasse", "Mês"]]
    df["Mês"] = datesRange.iloc[:, 0:1]
    df["Custo do Produto"] = pl_apl
    df["numero"] = df.index + 1
    df["numero"][df["numero"] > 12] = 12
    masquerede = masquerede[masquerede["Mês"].isin(df["numero"])]
    dic = masquerede.set_index("Mês").T.to_dict("list")
    df["Comissão Bruta"] = (
        df["numero"].map(dic).apply(lambda x: numpy.array(x[0], dtype=float))
    )
    df["Resulatdo Bruto"] = (df["Comissão Bruta"] / 100) * df["Custo do Produto"]
    df["Imposto"] = df["Resulatdo Bruto"] * 0.2
    df["Receita Líquida"] = df["Resulatdo Bruto"] - df["Imposto"]
    df["Resultado do Assessor"] = df["Receita Líquida"] * (roa_reps / 100)

    df["Comissão Bruta"] = df["Comissão Bruta"].apply(lambda x: "{:,.2f}%".format(x))

    st.dataframe(
        df[
            [
                "Mês",
                "Custo do Produto",
                "Comissão Bruta",
                "Imposto",
                "Receita Líquida",
                "Resultado assessor",
            ]
        ]
    )

    hide_dataframe_row_index = """
                <style>
                .row_heading.level0 {display:none}
                .blank {display:none}
                </style>
                """

    # Inject CSS with Markdown
    st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)

    sql = """UPDATE variaveis 
            SET categoria = ? ,
            ativo = ? ,
            empresa = ? ,
            data_venc = ? ,
            pl_aplicado = ? ,
            retorno = ? ,
            repasse = ? ,
            roa_head = ? ,
            roa_rec = ?,
            data_ativo = ?
            WHERE ativo_id = ?"""

    if st.button("Salvar"):
        cursor.execute(
            sql,
            (
                categoria,
                produto,
                empresa,
                data,
                pl_apl,
                0,
                roa_reps,
                0,
                0,
                data_inicial,
                v4,
            ),
        )
        con.commit()
        st.success("O ativo foi editado com sucesso")
        tm.sleep(1)
        with st.spinner("Redirecionando o Assessor para a Página de Ativos"):
            tm.sleep(1)
        nav_page("cliente_ativo")
else:
    st.error("Data de vencimento menor que a data de Início.")

st.markdown(
    """<hr style="height:1px;border:none;color:#9966ff;background-color:#9966ff;" /> """,
    unsafe_allow_html=True,
)

if st.button("Voltar"):
    nav_page("cliente_ativo")

st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
    footer {visibility: hidden;}
    .st-ip::after {
    background-color: rgb(153, 102, 255);
}
    .css-qriz5p:hover:enabled, .css-qriz5p:focus:enabled {
    color: rgb(255, 255, 255);
    background-color: rgb(153, 102, 255);
    transition: none 0s ease 0s;
    outline: none;
}
    img{
    background-color: rgb(14, 17, 23);
    }
    
    .st-fu {
    color: rgb(153, 102, 255);
}
</style>
""",
    unsafe_allow_html=True,
)


# cursor.close()
# con.close()
