import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import datetime as DT
import math
import time as tm
from func.redirect import nav_page
import pymysql
from database import con, cursor, moeda
import locale

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

# from func.connect import con, cursor


st.set_page_config(
    page_icon="invest_smart_logo.png",
    page_title="Simulador - Edit Ativos 0.15",
    initial_sidebar_state="collapsed",
)

col1, mid, col2 = st.columns([20, 1, 16])
with col1:
    st.empty()
with col2:
    st.image(
        "investsmart_endosso_horizontal_fundopreto.png",
    )

st.header("Editando um Ativo")


v4 = int(st.session_state.df_ativo.ativo_id[0])


v1_categ = st.session_state.df_ativo.Categoria[0]
v1_ativo = st.session_state.df_ativo.Ativo[0]
v1_data = st.session_state.df_ativo["Data de Vencimento"][0]
v1_pl_apl = st.session_state.df_ativo["PL Aplicado"][0]
v1_retorno = st.session_state.df_ativo.retorno[0]
v1_repasse = st.session_state.df_ativo.repasse[0]
v1_roa_head = st.session_state.df_ativo.roa_head[0]
v1_roa_rec = st.session_state.df_ativo.roa_rec[0]

st.markdown(
    """<hr style="height:1px;border:none;color:#9966ff;background-color:#9966ff;" /> """,
    unsafe_allow_html=True,
)

st.subheader("**Premissas**")

face = pd.read_excel("bd_base.xlsx")
face["Categoria"] = face["Categoria"].apply(lambda x: x.replace("_", " "))
face["ROA Cabeça"] = face["ROA Cabeça"] * 100.0
face["Roa Recorrente"] = face["Roa Recorrente"] * 100.0


categoria_list = list(face.Categoria.unique())


colNome1, colValue1 = st.columns(2)

with colNome1:
    categoria = st.selectbox(
        "Categoria: ", face.Categoria.unique(), index=categoria_list.index(v1_categ)
    )


with colValue1:
    pl_apl = st.number_input(
        "PL Aplicado (R$): ",
        min_value=0.0,
        format="%f",
        value=float(v1_pl_apl),
        step=1000.0,
    )
    st.text("R$" + locale.currency(pl_apl, grouping=True, symbol=None))


colNome2, colValue2 = st.columns(2)

try:
    ind = list(face.PRODUTOS[face["Categoria"] == categoria].unique()).index(v1_ativo)

    with colNome2:
        ativo = st.selectbox(
            "Ativo: ",
            list(face.PRODUTOS[face["Categoria"] == categoria].unique()),
            index=ind,
        )
except:
    with colNome2:
        ativo = st.selectbox(
            "Ativo: ",
            list(face.PRODUTOS[face["Categoria"] == categoria].unique()),
        )

with colValue2:
    retorno = st.number_input(
        "Retorno Esperado a.a. (%): ",
        min_value=0.0,
        max_value=100.0,
        value=float(v1_retorno),
        format="%f",
        step=1.0,
    )


colNome3, colValue3 = st.columns(2)
with colNome3:
    data = st.date_input(
        "Data de Vencimento: ",
        min_value=DT.date.today(),
        value=DT.datetime.strptime(v1_data[:10], "%Y-%m-%d"),
    )

with colValue3:
    roa_head = st.number_input(
        "ROA Cabeça (%): ",
        min_value=0.0,
        max_value=100.0,
        value=float(v1_roa_head),
        format="%.2f",
        step=0.01,
    )


colRoa_rec, colRepasse = st.columns(2)  # colRoa_rec, colCod, colRepasse = st.columns(3)

with colRoa_rec:
    roa_rec = st.number_input(
        "ROA Recorrente (%): ",
        min_value=0.0,
        format="%.2f",
        value=float(v1_roa_rec),
        max_value=100.0,
        step=0.1,
    )

# with colCod:
#     cod = st.text_input("Código/ Nome Cliente: ", value="John Doe")

with colRepasse:
    roa_reps = st.number_input(
        "Repasse Assessor (%): ",
        min_value=0.0,
        format="%f",
        value=float(v1_repasse),
        max_value=100.0,
        step=1.0,
    )

st.markdown(
    """<hr style="height:1px;border:none;color:#9966ff;background-color:#9966ff;" /> """,
    unsafe_allow_html=True,
)

dias = DT.datetime.strptime(str(data), "%Y-%m-%d") - DT.datetime.strptime(
    str(DT.date.today()), "%Y-%m-%d"
)
mes = round(dias.days / 30)


endDate = DT.datetime.strptime(str(data), "%Y-%m-%d")
startDate = DT.datetime.strptime(str(DT.date.today()), "%Y-%m-%d")

# Getting List of Days using pandas
if mes < 1:
    datesRange = pd.date_range(startDate, periods=1, freq="m")
    datesRange = list(datesRange)
else:
    datesRange = pd.date_range(startDate, periods=mes + 1, freq="m")
    datesRange = list(datesRange)

datesRange = [DT.datetime.strftime(x, "%b-%y") for x in datesRange]

datesRange = pd.DataFrame(datesRange)

############## calculator######################
pl = pl_apl + pl_apl * ((1.0 + (retorno / 100.0)) ** (1.0 / 12.0) - 1.0)

n = 0
l = mes + 1
pl_1 = []

for n in range(n, l):
    pl = pl_apl + pl_apl * ((1.0 + (retorno / 100.0)) ** (n / 12.0) - 1.0)
    pl_1.append(pl)
    n = +1
##########################################################################################
##########################VARIAVEIS DE INTERRESSE#########################################
##########################################################################################
roa_1 = roa_head + roa_rec

fat_1 = pl_apl * roa_1
fat = pl * roa_rec
imposto = -0.2 * fat
receit_liqu = math.fsum([fat, imposto])
result_assessor = receit_liqu * roa_reps
##########################################################################################
##########################################################################################

n = 0
roa_vini = [roa_1]
for n in range(n, l - 1):
    roa_vini.append(roa_rec)
    n += 1


dataframe = pd.DataFrame()

dataframe["Mês"] = datesRange.iloc[:, 0:1]
dataframe["PL Retido"] = pl_1
dataframe["Roa/Mês(%)"] = roa_vini
dataframe["Faturamento"] = dataframe["PL Retido"] * (dataframe["Roa/Mês(%)"] / 100)
dataframe["Imposto"] = dataframe["Faturamento"] * -0.2
dataframe["Receita Líquida"] = dataframe["Faturamento"] + dataframe["Imposto"]
dataframe["Resultado assessor"] = dataframe["Receita Líquida"] * (roa_reps / 100)

moeda(
    dataframe,
    [
        "PL Retido",
        "Faturamento",
        "Imposto",
        "Receita Líquida",
        "Resultado assessor",
    ],
)

dataframe["Roa/Mês(%)"] = dataframe["Roa/Mês(%)"].apply(lambda x: "{:,.2f}%".format(x))

st.dataframe(dataframe)


sql = """UPDATE variaveis 
        SET categoria = ? ,
        ativo = ? ,
        data_venc = ? ,
        pl_aplicado = ? ,
        retorno = ? ,
        repasse = ? ,
        roa_head = ? ,
        roa_rec = ?
        WHERE ativo_id = ?"""

if st.button("Salvar"):
    cursor.execute(
        sql,
        (categoria, ativo, data, pl_apl, retorno, roa_reps, roa_head, roa_rec, v4),
    )
    con.commit()
    st.success("O ativo foi editado com sucesso")
    tm.sleep(1)
    with st.spinner("Redirecionando o Assessor para a Página de Ativos"):
        tm.sleep(1)
    nav_page("cliente_ativo")

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
</style>
""",
    unsafe_allow_html=True,
)


# cursor.close()
# con.close()
