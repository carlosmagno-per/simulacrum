import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import datetime as DT
import math
import time as tm
from func.redirect import nav_page
from sqlalchemy import create_engine
from database import con, cursor, moeda, base_df
import locale
import streamlit.components.v1 as components
import plotly.express as px


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
    st.image("investsmart_endosso_horizontal_fundopreto.png", width=270)


st.markdown(
    """<hr style="height:1px;border:none;color:#9966ff;background-color:#9966ff;" /> """,
    unsafe_allow_html=True,
)

prem, table = st.columns(2)
with prem:
    st.subheader("**Premissas**")

    face = pd.read_excel("bd_base_v3.xlsx")
    face["Categoria"] = face["Categoria"].apply(lambda x: x.replace("_", " "))
    face["ROA Cabeça"] = face["ROA Cabeça"] * 100.0
    face["Roa Recorrente"] = face["Roa Recorrente"] * 100.0
    v3 = int(st.session_state.df_cliente.client_id[0])
    name_v1 = st.session_state.df_cliente["Nome do Cliente"][0]

    # st.write(v3)
    # st.write(name_v1)
    good_categ = ["Fundos","Previdencia"]
    

    colNome1, colValue1 = st.columns(2)

    with colNome1:
        categoria = st.selectbox(
            "Categoria: ",
            face.sort_values(by="Categoria").Categoria.unique(),
        )
    if categoria in good_categ:
        with colValue1:
            subcategoria = st.selectbox(
                "Subcategoria: ",
                face.sort_values(by="Subcategoria").Subcategoria[face["Categoria"] == categoria].unique(),
            )  
            

        colNome2, colValue2 = st.columns(2)

        with colNome2:
            ativo = st.selectbox(
                    "Ativo: ", list(face.sort_values(by="PRODUTOS").PRODUTOS[(face["Categoria"] == categoria) & (face["Subcategoria"] == subcategoria)].unique())
                )
            

        with colValue2:
            pl_apl = st.number_input(
                "PL Aplicado (R$): ",
                min_value=0.0,
                format="%f",
                value=3000000.0,
                step=1000.0,
            )
            st.text("R$" + locale.currency(pl_apl, grouping=True, symbol=None))
            # retorno = st.number_input(
            #     "Retorno Esperado a.a. (%): ",
            #     min_value=0.0,
            #     max_value=100.0,
            #     value=12.0,
            #     format="%f",
            #     step=1.0,
            # )

        colNome3, colValue3 = st.columns(2)
        with colNome3:
            data_inicial = st.date_input("Data de Início: ", min_value=DT.date.today())

        with colValue3:
            data = st.date_input("Data de Vencimento: ", min_value=DT.date.today())

        colroa_head, colRoa_rec = st.columns(2)
        #colroa_head, colRoa_rec, colRepasse = st.columns(3)

        with colRoa_rec:
            roa_rec = st.number_input(
                "ROA Recorrente (%): ",
                min_value=0.0,
                format="%.2f",
                value=float(face["Roa Recorrente"][face["PRODUTOS"] == ativo]),
                max_value=100.0,
                step=0.1,
            )

        with colroa_head:
            roa_head = st.number_input(
                "ROA Cabeça (%): ",
                min_value=0.0,
                max_value=100.0,
                value=float(face["ROA Cabeça"][face["PRODUTOS"] == ativo]),
                format="%.2f",
                step=0.01,
            )

        # with colRepasse:
        #     roa_reps = st.number_input(
        #         "Repasse Assessor (%): ",
        #         min_value=0.0,
        #         format="%f",
        #         value=50.0,
        #         max_value=100.0,
        #         step=1.0,
        #     )
        roa_reps = 50.0
        retorno= 0.0
        
    
    else:
        with colValue1:
            ativo = st.selectbox(
                    "Ativo: ", list(face.sort_values(by="PRODUTOS").PRODUTOS[(face["Categoria"] == categoria)].unique())
                )
            
        pl_apl = st.number_input(
            "PL Aplicado (R$): ",
            min_value=0.0,
            format="%f",
            value=3000000.0,
            step=1000.0,
        )
        st.text("R$" + locale.currency(pl_apl, grouping=True, symbol=None))

        colNome3, colValue3 = st.columns(2)
        with colNome3:
            data_inicial = st.date_input("Data de Início: ", min_value=DT.date.today())

        with colValue3:
            data = st.date_input("Data de Vencimento: ", min_value=DT.date.today())

        colroa_head, colRoa_rec = st.columns(2)
        #colroa_head, colRoa_rec, colRepasse = st.columns(3)

        with colRoa_rec:
            roa_rec = st.number_input(
                "ROA Recorrente (%): ",
                min_value=0.0,
                format="%.2f",
                value=float(face["Roa Recorrente"][face["PRODUTOS"] == ativo]),
                max_value=100.0,
                step=0.1,
            )

        with colroa_head:
            roa_head = st.number_input(
                "ROA Cabeça (%): ",
                min_value=0.0,
                max_value=100.0,
                value=float(face["ROA Cabeça"][face["PRODUTOS"] == ativo]),
                format="%.2f",
                step=0.01,
            )
        roa_reps = 50.0
        retorno= 0.0

st.markdown(
    """<hr style="height:1px;border:none;color:#9966ff;background-color:#9966ff;" /> """,
    unsafe_allow_html=True,
)

volte, salve_v2, espaco_10= st.columns([5,5,15])
with volte:
    if st.button("Voltar"):
        nav_page("cliente_wide")
# st.markdown(
#     """<hr style="height:1px;border:none;color:#9966ff;background-color:#9966ff;" />
#     <p > Visualização do ativo por uma tabela </p>
#     """,
#     unsafe_allow_html=True,
# )
with table:
    st.subheader("**Fluxo de Comissão**")
    if data > data_inicial:

        dataframe = base_df(
            data, data_inicial, pl_apl, retorno, roa_head, roa_rec, roa_reps
        )

        st.dataframe(dataframe)

        sql = "INSERT INTO variaveis (client_id, empresa, categoria, ativo, data_venc, pl_aplicado, retorno, repasse, roa_head, roa_rec, data_ativo) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)"
        # today = DT.datetime.strftime(DT.datetime.today(), "%Y-%m-%d")
        with salve_v2:
            if st.button("Salvar"):
                cursor.execute(
                    sql,
                    (
                        v3,
                        "INVESTSMART",
                        categoria,
                        ativo,
                        data,
                        pl_apl,
                        retorno,
                        roa_reps,
                        roa_head,
                        roa_rec,
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


# if st.button("Voltar"):
#     nav_page("cliente_ativo")
# if authenticator.logout("Logout"):
#     nav_page("Home")

# st.markdown("[Pula lá para cima](#hyper_v1)", unsafe_allow_html=True)



st.markdown(
    """
<style>
    .st-bw {
    background-color: rgb(63, 63, 63);
    }
    
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
    img {
    background-color: rgb(18, 19, 18);
    }


</style>
""",
    unsafe_allow_html=True,
)

# cursor.close()
# con.close()
