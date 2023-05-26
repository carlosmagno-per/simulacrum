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
from database import moeda, besmart_base, PositivadorBitrix
import locale
import requests

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

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
    esquerda, direita  = st.columns([5, 4])
    with direita:
        if st.button('Logout',key='logout6'):
            st.session_state["logout"] =None
            if st.session_state["logout"]==None:
                nav_page('')


st.markdown(
    """<hr style="height:1px;border:none;color:#9966ff;background-color:#9966ff;" /> """,
    unsafe_allow_html=True,
)
prem, table = st.columns(2)
with prem:
    st.subheader("**Premissas**")

    face = pd.read_excel("base_besmart_v3.xlsx")
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
            face.sort_values(by="Empresa").Empresa.unique(),
        )

    with colValue1:
        categoria = st.selectbox(
            "Categoria: ",
            list(face.sort_values(by="Categoria").Categoria[face["Empresa"] == empresa].unique()),
        )

    colvalor, colpain = st.columns(2)

    with colpain:
        produto = st.selectbox(
            "Produto: ",
            list(face.sort_values(by="Produto").Produto[(face["Empresa"] == empresa)&(face["Categoria"] == categoria)].unique()),
        )
    with colvalor:
        if produto == "Icatu (até R$299,99)":
            pl_apl = st.number_input(
                "Valor do Produto (R$): ",
                min_value=0.0,
                max_value=299.00,
                format="%f",
                value=100.00,
                step=100.0,
            )
        elif produto == "Icatu (R$300,00 - R$599,99)":
            pl_apl = st.number_input(
                "Valor do Produto (R$): ",
                min_value=300.0,
                max_value=599.00,
                format="%f",
                value=300.00,
                step=100.0,
            )
        elif produto == "Icatu (apartir de R$600,00)":
            pl_apl = st.number_input(
                "Valor do Produto (R$): ",
                min_value=600.0,
                format="%f",
                value=600.00,
                step=100.0,
            )
        elif produto == "Sulamérica Prestige (até R$5000,00)":
            pl_apl = st.number_input(
                "Valor do Produto (R$): ",
                min_value=0.0,
                max_value=5000.00,
                format="%f",
                value=1000.00,
                step=100.0,
            )
        else:
            pl_apl = st.number_input(
                "Valor do Produto (R$): ",
                min_value=0.0,
                format="%f",
                value=25000.0,
                step=1000.0,
            )
        st.text("R$" + locale.currency(pl_apl, grouping=True, symbol=None))

    colNome3, colValue3 = st.columns(2)
    with colNome3:
        data_inicial = st.date_input("Data de Início: ", min_value=DT.date.today())

    with colValue3:
        if produto == "Icatu Esporádico" or produto == "Sulamérica Prestige Esporádico":
            data = st.date_input(
                "Data de Vencimento: ",
                min_value=data_inicial,
                max_value=data_inicial + DT.timedelta(days=15),
            )
        else:
            data = st.date_input(
                "Data de Vencimento: ",
                min_value=DT.date.today(),
            )

    dias = DT.datetime.strptime(str(data), "%Y-%m-%d") - DT.datetime.strptime(
        str(data_inicial), "%Y-%m-%d"
    )
    mes = round(dias.days / 30)

    if mes < 1:
        mes = 1
    else:
        mes = mes

   
    if empresa != "Imóveis":
 
        roa_reps= 50
    else:
        roa_reps = 100
    roa_rec = 0


bad_prod = [
    "GARSON - Antecipação de Recebiveis",
    "Operações Estruturadas com Garantia Reais(Bens e Recebíveis)",
    "Ulend - Capital de Giro Clean",
    "Precato",
    "LTZ Capital",
    "Acredite",
    "EasyPrec",
    "JEEVES - Capital de Giro Clean",
    "Planta Consultoria - Agro",
    "UHY - Crédito PJ",
    "LISTO - Antecipação de maquininhas CDC Capital de Giro até 24x",
    "RM2 - Antacipação de Recebiveis",
    "LOARA - PJ",
    "BANEFORT - PJ",
]

st.markdown(
    """<hr style="height:1px;border:none;color:#9966ff;background-color:#9966ff;" /> """,
    unsafe_allow_html=True,
)

volte, salve_v2, espaco_10= st.columns([5,5,15])
with volte:
    if st.button("Voltar"):
        nav_page("cliente_wide")


if produto in bad_prod:
    with table:
        st.text("")
        st.text("")
        st.text("")
        st.text("")
        st.text("")
        st.text("")
        st.text("")
        st.text("")
        st.text("")
        st.text("")
        st.text("")
        st.text("")
        st.warning(
            "Esse produto apresenta um calculo de dificil simulação ou com uma peculiaridade, por favor busque a ajuda de um dos especialista"
        )
else:
    with table:
        st.subheader("**Fluxo de Comissão**")
        if data > data_inicial:
            if produto == "Lançamento":
                df = besmart_base(
                    data,
                    data_inicial,
                    face,
                    empresa,
                    categoria,
                    produto,
                    pl_apl,
                    roa_reps,
                    roa_rec,
                    corretag=0.04
                )
                
            elif produto == "Consultoria e Incorporação":
                df = besmart_base(
                    data,
                    data_inicial,
                    face,
                    empresa,
                    categoria,
                    produto,
                    pl_apl,
                    roa_reps,
                    roa_rec,
                    corretag=0.04
                )
            
            elif produto == "Avaliação":
                df = besmart_base(
                    data,
                    data_inicial,
                    face,
                    empresa,
                    categoria,
                    produto,
                    pl_apl,
                    roa_reps,
                    roa_rec,
                    impost=0
                )
            elif categoria == "Imóveis Prontos":
                df = besmart_base(
                    data,
                    data_inicial,
                    face,
                    empresa,
                    categoria,
                    produto,
                    pl_apl,
                    roa_reps,
                    roa_rec,
                    corretag=0.05
                )
            
            else:
                df = besmart_base(
                    data,
                    data_inicial,
                    face,
                    empresa,
                    categoria,
                    produto,
                    pl_apl,
                    roa_reps,
                    roa_rec,
                )

            try:
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
            except:
                st.dataframe(
                    df[
                        [
                            "Mês",
                            "Custo do Produto",
                            "Corretagem Bruta",
                            "Resultado Bruto",
                            "Imposto",
                            "Corretagem Líquida",
                            "Comissão Bruta",
                            "Resultado assessor",
                        ]
                    ]
                )
           
            with salve_v2:
                if st.button("Salvar"):
                  
                    roa_head=0
                    retorno=0
                    url = "https://"+st.secrets.domain+"rest/"+st.secrets.bignumber+"/"+st.secrets.cod_shhh+"/crm.deal.add.json?fields["+st.secrets.VAR4+f"]={categoria}&fields["+st.secrets.VAR5+f"]={produto}&fields["+st.secrets.VAR6+f"]={roa_head}&fields["+st.secrets.VAR7+f"]={roa_rec}&fields["+st.secrets.VAR8+f"]={pl_apl}&fields["+st.secrets.VAR9+f"]={data_inicial}&fields["+st.secrets.VAR10+f"]={data}&fields["+st.secrets.VAR11+f"]={v3}&fields["+st.secrets.VAR12+f"]={empresa}&fields["+st.secrets.VAR13+f"]={retorno}&fields["+st.secrets.VAR14+f"]={roa_reps}&fields["+st.secrets.category+"]="+st.secrets.arabian

                    payload = {}
                    headers = {
                    'Cookie': 'BITRIX_SM_SALE_UID=0; qmb=0.'
                    }

                    response = requests.request("POST", url, headers=headers, data=payload)
                    st.success("O ativo foi editado com sucesso")
                    tm.sleep(1)
                    with st.spinner("Redirecionando o Assessor para a Página de Ativos"):
                        tm.sleep(1)
                    nav_page("cliente_wide")
        else:
            st.error("Data de vencimento tem que ser maior que a data de Início.")

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
    img{
    background-color: rgb(18, 19, 18);
    }

</style>
""",
    unsafe_allow_html=True,
)

