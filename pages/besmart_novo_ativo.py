import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import datetime as DT
import math
import time as tm
import numpy
from func.redirect import nav_page
from sqlalchemy import create_engine
from database import con, cursor, moeda, besmart_base
import locale

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

# from func.connect import con, cursor


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
    st.image("BeSmart_Logos_AF_horizontal__branco.png", width=270)


st.markdown(
    """<hr style="height:1px;border:none;color:#9966ff;background-color:#9966ff;" /> """,
    unsafe_allow_html=True,
)
prem, table = st.columns(2)
with prem:
    st.subheader("**Premissas**")

    face = pd.read_excel("base_besmart.xlsx")
    face["Categoria"] = face["Categoria"].apply(lambda x: x.replace("_", " "))
    face["Produto"] = face["Produto"].apply(lambda x: x.replace("_", " "))
    face["porcem_repasse"] = face["porcem_repasse"] * 100.0
    v3 = int(st.session_state.df_cliente.client_id[0])
    name_v1 = st.session_state.df_cliente["Nome do Cliente"][0]

    # st.write(v3)
    # st.write(name_v1)

    colNome1, colValue1 = st.columns(2)

    with colNome1:
        empresa = st.selectbox(
            "Empresa, Be.Smart: ",
            face.Empresa.unique(),
        )

    with colValue1:
        categoria = st.selectbox(
            "Categoria: ",
            list(face.Categoria[face["Empresa"] == empresa].unique()),
        )

    colvalor, colpain = st.columns(2)
    with colvalor:
        pl_apl = st.number_input(
            "Valor do Produto (R$): ",
            min_value=0.0,
            format="%f",
            value=10000.0,
            step=1000.0,
        )
        st.text("R$" + locale.currency(pl_apl, grouping=True, symbol=None))

    with colpain:
        produto = st.selectbox(
            "Produto: ",
            list(face.Produto[face["Categoria"] == categoria].unique()),
        )

    colNome3, colValue3 = st.columns(2)
    with colNome3:
        data_inicial = st.date_input("Data de Início: ", min_value=DT.date.today())

    with colValue3:
        data = st.date_input("Data de Vencimento: ", min_value=DT.date.today())

    dias = DT.datetime.strptime(str(data), "%Y-%m-%d") - DT.datetime.strptime(
        str(data_inicial), "%Y-%m-%d"
    )
    mes = round(dias.days / 30)

    if mes < 1:
        mes = 1
    else:
        mes = mes

    # colcomi, colrepas = st.columns(2)
    # with colcomi:
    #     comissao = st.number_input(
    #         "Comissão Bruta (%): ",
    #         min_value=0.0,
    #         max_value=100.0,
    #         value=float(
    #             face["porcem_repasse"][
    #                 (face["Empresa"] == empresa)
    #                 & (face["Categoria"] == categoria)
    #                 & (face["Produto"] == produto)
    #                 & face["Mês"]
    #                 == mes
    #             ].iloc[0]
    #         ),
    #         format="%.2f",
    #         step=0.01,
    #     )

    # with colrepas:
    roa_reps = st.number_input(
        "Repasse Assessor (%): ",
        min_value=0.0,
        format="%f",
        value=50.0,
        max_value=100.0,
        step=1.0,
    )
# ((valor * com_brut) - 0.2 * (valor * com_brut)) * repas_asse

# st.markdown(
#     """<hr style="height:1px;border:none;color:#9966ff;background-color:#9966ff;" />
#     <p > Visualização do produto por uma tabela </p>
#     """,
#     unsafe_allow_html=True,
# )


with table:
    st.subheader("**Visualização do ativo por uma tabela**")
    if data > data_inicial:
        df = besmart_base(
            data, data_inicial, face, empresa, categoria, produto, pl_apl, roa_reps
        )

        # dias = DT.datetime.strptime(str(data), "%Y-%m-%d") - DT.datetime.strptime(
        #     str(data_inicial), "%Y-%m-%d"
        # )
        # mes = round(dias.days / 30)

        # endDate = DT.datetime.strptime(str(data), "%Y-%m-%d")
        # startDate = DT.datetime.strptime(str(data_inicial), "%Y-%m-%d")

        # # Getting List of Days using pandas
        # if mes < 1:
        #     datesRange = pd.date_range(startDate, periods=1, freq="m")
        #     datesRange = list(datesRange)
        # else:
        #     datesRange = pd.date_range(startDate, periods=mes + 1, freq="m")
        #     datesRange = list(datesRange)

        # datesRange = [DT.datetime.strftime(x, "%b-%y") for x in datesRange]

        # datesRange = pd.DataFrame(datesRange)

        # df = pd.DataFrame()
        # masquerede = face[
        #     (face["Empresa"] == empresa)
        #     & (face["Categoria"] == categoria)
        #     & (face["Produto"] == produto)
        # ][["porcem_repasse", "Mês"]]
        # df["Mês"] = datesRange.iloc[:, 0:1]
        # df["Custo do Produto"] = pl_apl
        # df["numero"] = df.index + 1
        # df["numero"][df["numero"] > 12] = 12
        # masquerede = masquerede[masquerede["Mês"].isin(df["numero"])]
        # dic = masquerede.set_index("Mês").T.to_dict("list")
        # df["Comissão Bruta"] = (
        #     df["numero"].map(dic).apply(lambda x: numpy.array(x[0], dtype=float))
        # )
        # df["Resulatdo Bruto"] = (df["Comissão Bruta"] / 100) * df["Custo do Produto"]
        # df["Imposto"] = df["Resulatdo Bruto"] * 0.2
        # df["Receita Líquida"] = df["Resulatdo Bruto"] - df["Imposto"]
        # df["Resultado do Assessor"] = df["Receita Líquida"] * (roa_reps / 100)

        # df["Comissão Bruta"] = df["Comissão Bruta"].apply(lambda x: "{:,.2f}%".format(x))

        st.dataframe(
            df[
                [
                    "Mês",
                    "Custo do Produto",
                    "Comissão Bruta",
                    "Resultado Bruto",
                    "Receita Líquida",
                    "Imposto",
                    "Resultado assessor",
                ]
            ]
        )
        # st.dataframe(masquerede)

        sql = "INSERT INTO variaveis (client_id, empresa, categoria, ativo, data_venc, pl_aplicado, retorno, repasse, roa_head, roa_rec, data_ativo) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)"
        # today = DT.datetime.strftime(DT.datetime.today(), "%Y-%m-%d")

        if st.button("Salvar"):
            cursor.execute(
                sql,
                (
                    v3,
                    empresa,
                    categoria,
                    produto,
                    data,
                    pl_apl,
                    0,
                    roa_reps,
                    0,
                    0,
                    data_inicial,
                ),
            )
            con.commit()
            st.success("O ativo foi editado com sucesso")
            tm.sleep(1)
            with st.spinner("Redirecionando o Assessor para a Página de Ativos"):
                tm.sleep(1)
            nav_page("cliente_wide")
    else:
        st.error("Data de vencimento tem que ser maior que a data de Início.")

st.markdown(
    """<hr style="height:1px;border:none;color:#9966ff;background-color:#9966ff;" /> """,
    unsafe_allow_html=True,
)

# if st.button("Voltar"):
#     nav_page("cliente_ativo")
# if authenticator.logout("Logout"):
#     nav_page("Home")
if st.button("Voltar"):
    nav_page("cliente_wide")


# st.markdown("[Pula lá para cima](#hyper_v1)", unsafe_allow_html=True)

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

    .st-fu {
    color: rgb(153, 102, 255);
}

.st-hd::after {
    background-color: rgb(153, 102, 255);
}

.st-ha::after {
    border-color: transparent;
}

</style>
""",
    unsafe_allow_html=True,
)

# cursor.close()
# con.close()
