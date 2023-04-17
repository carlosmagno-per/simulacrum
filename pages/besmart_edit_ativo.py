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
    page_title="Simulador - Edit Ativos 0.25",
    initial_sidebar_state="collapsed",
    layout="wide",
)

col1, mid, col2 = st.columns([20, 2, 4])
with col1:
    st.header("Editando um Ativo")
with col2:
    st.image("BeSmart_Logos_AF_horizontal__branco.png", width=270)


v4 = int(st.session_state.df_ativo.ativo_id[0])

v1_empresa = st.session_state.df_ativo.Empresa.iloc[0]
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

st.markdown(
    """<hr style="height:1px;border:none;color:#9966ff;background-color:#9966ff;" /> """,
    unsafe_allow_html=True,
)

prem, table = st.columns(2)
with prem:
    st.subheader("**Premissas**")

    face = pd.read_excel("base_besmart_v2.xlsx")
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
    try:
        ind_2 = list(face.Produto[face["Categoria"] == categoria].unique()).index(
            v1_ativo
        )
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
    with colvalor:
        if produto == "Icatu (até R$299,99)":
            pl_apl = st.number_input(
                "Valor do Produto (R$): ",
                min_value=0.0,
                # max_value=299.00,
                format="%f",
                value=float(v1_pl_apl),
                step=100.0,
            )
        elif produto == "Icatu (R$300,00 - R$599,99)":
            pl_apl = st.number_input(
                "Valor do Produto (R$): ",
                min_value=300.0,
                # max_value=599.00,
                format="%f",
                value=float(v1_pl_apl),
                step=100.0,
            )
        elif produto == "Icatu (apartir de R$600,00)":
            pl_apl = st.number_input(
                "Valor do Produto (R$): ",
                min_value=600.0,
                format="%f",
                value=float(v1_pl_apl),
                step=100.0,
            )
        elif produto == "Sulamérica Prestige (até R$5000,00)":
            pl_apl = st.number_input(
                "Valor do Produto (R$): ",
                min_value=0.0,
                # max_value=5000.00,
                format="%f",
                value=float(v1_pl_apl),
                step=100.0,
            )
        else:
            pl_apl = st.number_input(
                "Valor da Venda (R$): ",
                min_value=0.0,
                format="%f",
                value=float(v1_pl_apl),
                step=1000.0,
            )
        st.text("R$" + locale.currency(pl_apl, grouping=True, symbol=None))

    colNome3, colValue3 = st.columns(2)
    with colNome3:
        data_inicial = st.date_input(
            "Data de Início: ",
            # min_value=DT.date.today()
            value=DT.datetime.strptime(v1_data_inicio[:10], "%Y-%m-%d"),
        )

    with colValue3:
        if produto == "Icatu Esporádico" or produto == "Sulamérica Prestige Esporádico":
            data = st.date_input(
                "Data de Vencimento: ",
                min_value=data_inicial,
                max_value=data_inicial + DT.timedelta(days=15),
                value=data_inicial + DT.timedelta(days=15),
            )
        else:
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

    if produto == "PJ":
        colrepas, situation = st.columns(2)
        with colrepas:
            roa_reps = st.number_input(
                "Repasse Assessor (%): ",
                min_value=0.0,
                format="%f",
                value=50.0,
                max_value=100.0,
                step=1.0,
            )
        with situation:
            roa_rec = st.selectbox("Corretagem Vitalícia (%)", [5, 2, 4, 0])
            if roa_rec == 5:
                st.write("Valor comum para a empresa Assim")
            elif roa_rec == 2:
                st.write(
                    "Valor comum para as empresas Amil, Bradesco, Sulámerica, Golden Cross OU Intermédica"
                )
            elif roa_rec == 4:
                st.write("Valor comum para a empresa Porto Seguro")
            elif roa_rec == 0:
                st.write("Valor comum para as empresas Unimed OU Omint")
    else:
        roa_reps = st.number_input(
            "Repasse Assessor (%): ",
            min_value=0.0,
            format="%f",
            value=50.0,
            max_value=100.0,
            step=1.0,
        )
        roa_rec = 0

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
# st.markdown(
#     """<hr style="height:1px;border:none;color:#9966ff;background-color:#9966ff;" />
#     <p > Visualização do produto por uma tabela </p>
#     """,
#     unsafe_allow_html=True,
# )
with table:
    st.header("Visualização do produto por uma tabela")

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
        if produto != "PJ":
            masquerede = face[
                (face["Empresa"] == empresa)
                & (face["Categoria"] == categoria)
                & (face["Produto"] == produto)
            ][["porcem_repasse", "Mês"]]
            df["Mês"] = datesRange.iloc[:, 0:1]
            df["Custo do Produto"] = pl_apl
            df["numero"] = df.index + 1
            masquerede = masquerede[masquerede["Mês"].isin(df["numero"])]
            dic = masquerede.set_index("Mês").T.to_dict("list")
            df["numero"][df["numero"] > max(masquerede["Mês"])] = max(masquerede["Mês"])
            df["Comissão Bruta"] = (
                df["numero"]
                .map(dic)
                .fillna(method="ffill")
                .apply(lambda x: numpy.array(x[0], dtype=float))
            )
            df["Resultado Bruto"] = (df["Comissão Bruta"] / 100) * df[
                "Custo do Produto"
            ]
            df["Imposto"] = df["Resultado Bruto"] * 0.2
            df["Receita Líquida"] = df["Resultado Bruto"] - df["Imposto"]
            df["Resultado do Assessor"] = df["Receita Líquida"] * (roa_reps / 100)

            df["Comissão Bruta"] = df["Comissão Bruta"].apply(
                lambda x: "{:,.2f}%".format(x)
            )
        else:
            masquerede = face[
                (face["Empresa"] == empresa)
                & (face["Categoria"] == categoria)
                & (face["Produto"] == produto)
            ][["porcem_repasse", "Mês"]]
            df["Mês"] = datesRange.iloc[:, 0:1]
            df["Custo do Produto"] = pl_apl
            df["numero"] = df.index + 1
            df["numero"][df["numero"] > max(masquerede["Mês"])] = max(masquerede["Mês"])
            masquerede = masquerede[masquerede["Mês"].isin(df["numero"])]
            dic = masquerede.set_index("Mês").T.to_dict("list")
            df["Comissão Bruta"] = (
                df["numero"].map(dic).apply(lambda x: numpy.array(x[0], dtype=float))
            )
            df["Comissão Bruta"][max(masquerede["Mês"]) :] = roa_rec
            df["Resultado Bruto"] = (df["Comissão Bruta"] / 100) * df[
                "Custo do Produto"
            ]
            df["Imposto"] = df["Resultado Bruto"] * 0.2
            df["Receita Líquida"] = df["Resultado Bruto"] - df["Imposto"]
            df["Resultado do Assessor"] = df["Receita Líquida"] * (roa_reps / 100)

            df["Comissão Bruta"] = df["Comissão Bruta"].apply(
                lambda x: "{:,.2f}%".format(x)
            )

        st.dataframe(
            df[
                [
                    "Mês",
                    "Custo do Produto",
                    "Comissão Bruta",
                    "Resultado Bruto",
                    "Receita Líquida",
                    "Imposto",
                    "Resultado do Assessor",
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
            nav_page("cliente_wide")
    else:
        st.error("Data de vencimento menor que a data de Início.")

st.markdown(
    """<hr style="height:1px;border:none;color:#9966ff;background-color:#9966ff;" /> """,
    unsafe_allow_html=True,
)

# if st.button("Voltar"):
#     nav_page("cliente_ativo")

if st.button("Voltar"):
    nav_page("cliente_wide")

st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
    footer {visibility: hidden;}

    .css-qriz5p:hover:enabled, .css-qriz5p:focus:enabled {
    color: rgb(255, 255, 255);
    background-color: rgb(153, 102, 255);
    transition: none 0s ease 0s;
    outline: none;
}
    img{
    background-color: rgb(14, 17, 23);
    }

</style>
""",
    unsafe_allow_html=True,
)


# cursor.close()
# con.close()
