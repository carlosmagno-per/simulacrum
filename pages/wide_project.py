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
from database import base_df, besmart_base, moeda, PositivadorBitrix
import locale
from msal_streamlit_authentication import msal_authentication
import requests


locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

st.set_page_config(
    page_icon="invest_smart_logo.png",
    page_title="Simulador - Clientes 0.25",
    initial_sidebar_state="collapsed",
    layout="wide",
)

#df = pd.read_sql("SELECT * FROM cliente", con)
lista=list(PositivadorBitrix().get_data_default(6)[st.secrets.id])
df = PositivadorBitrix().get_data_custom(lista)
#st.dataframe(df)
df = df.rename(columns={st.secrets.deal:'client_id',st.secrets.VAR1:'sigla',st.secrets.VAR2:'nome_client',st.secrets.VAR3:'data_cliente'})

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
    esquerda, direita  = st.columns([5, 4])
    with direita:
        if st.button('Logout',key='logout1'):
            st.session_state["logout"] =None
            if st.session_state["logout"]==None:
                nav_page('')

st.markdown(
    """
    <hr style="height:1px;border:none;color:#9966ff;background-color:#9966ff;" /> 
    """,
    unsafe_allow_html=True,
)


#######################################################################################
############################ METRICS USADAS NOS BIGNUMBERS ############################
#######################################################################################

vazio_nulo ,pl, retorno, ano1_avg, ano2_avg  = st.columns([1,5, 5, 5, 3])

list_client_id = dark["client_id"].unique().astype(int)
list_client_id = list(list_client_id)

#fair = pd.read_sql("SELECT * FROM variaveis", con)
lista2=list(PositivadorBitrix().get_data_default(30)["ID"])
fair = PositivadorBitrix().get_data_all()
fair = fair.rename(columns={
    st.secrets.VAR11:'client_id',
    st.secrets.VAR12:'empresa',
    st.secrets.VAR4:'categoria',
    st.secrets.VAR5:'ativo',
    st.secrets.VAR8:'pl_aplicado',
    st.secrets.VAR13:'retorno',
    st.secrets.VAR14:'repasse',
    st.secrets.VAR6:'roa_head',
    st.secrets.VAR7:'roa_rec',
    st.secrets.VAR9:'data_ativo',
    st.secrets.VAR10:'data_venc',
    st.secrets.deal:'ativo_id',
    })
fair = fair.dropna()
fair['pl_aplicado']= fair['pl_aplicado'].astype(int)
fair['client_id']= fair['client_id'].astype(int)
fair['retorno']= fair['retorno'].astype(float)
fair['repasse']= fair['repasse'].astype(float)
fair['roa_head']= fair['roa_head'].astype(float)
fair['roa_rec']= fair['roa_rec'].astype(float)
fair['ativo_id']= fair['ativo_id'].astype(int)
fair = fair[fair.client_id.isin(list_client_id)]

#st.dataframe(fair)
dicio = fair.groupby("client_id")["pl_aplicado"].sum()
dark["PL Aplicado"] = (
    df["client_id"]
    .map(dicio)
    .apply(lambda x: locale.currency(x, grouping=True, symbol=True))
)
#st.dataframe(dark)
dark["PL Aplicado"] = dark["PL Aplicado"].replace("R$ nan", "R$ 0,00")

dark["Investimentos"] = (
    df["client_id"]
    .map(fair[fair.empresa=='INVESTSMART'].groupby("client_id")["pl_aplicado"].sum())
    .apply(lambda x: locale.currency(x, grouping=True, symbol=True))
)
dark["Investimentos"] = dark["Investimentos"].replace("R$ nan", "R$ 0,00")

fair["karma"] = [
    "InvestSmart" if x == "INVESTSMART" else "BeSmart" for x in fair["empresa"]
]
#st.dataframe(fair)
pl.metric(
    "Total do Portifólio",
    "R$ " + locale.currency(fair[fair.empresa=='INVESTSMART'].pl_aplicado.sum(), grouping=True, symbol=None)[:-3],
)

if fair.pl_aplicado.sum() == 0:
    dark["Qnt. Ativos InvestSmart"] = 0
    dark["Qnt. Produtos BeSmart"] = 0
    dark["PL Aplicado"] = 0

else:
    try:
        dark["Qnt. Ativos InvestSmart"] = [
            fair[fair["client_id"] == x].value_counts("karma")["InvestSmart"]
            if x in fair["client_id"].unique()
            else 0
            for x in dark["client_id"].unique()
        ]
        dark["Qnt. Produtos BeSmart"] = [
            fair[fair["client_id"] == x]
            .value_counts("karma")
            .reindex(fair.karma.unique(), fill_value=0)
            .sum()
            - fair[fair["client_id"] == x]
            .value_counts("karma")
            .reindex(fair.karma.unique(), fill_value=0)["InvestSmart"]
            if x in fair["client_id"].unique()
            else 0
            for x in dark["client_id"].unique()
        ]
    except:
        dark["Qnt. Produtos BeSmart"] = [
            fair[fair["client_id"] == x].value_counts("karma").reindex(fair.karma.unique(), fill_value=0)["BeSmart"]
            if x in fair["client_id"].unique()
            else 0
            for x in dark["client_id"].unique()
        ]

        dark["Qnt. Ativos InvestSmart"] = [
            fair[fair["client_id"] == x]
            .value_counts("karma")
            .reindex(fair.karma.unique(), fill_value=0)
            .sum()
            - fair[fair["client_id"] == x]
            .value_counts("karma")
            .reindex(fair.karma.unique(), fill_value=0)["BeSmart"]
            if x in fair["client_id"].unique()
            else 0
            for x in dark["client_id"].unique()
        ]



smart = pd.DataFrame(columns=["Mês", "Resultado assessor"])


face = pd.read_excel("base_besmart_v3.xlsx")
face["Categoria"] = face["Categoria"].apply(lambda x: x.replace("_", " "))
face["Produto"] = face["Produto"].apply(lambda x: x.replace("_", " "))
face["porcem_repasse"] = face["porcem_repasse"] * 100.0

for i in fair["ativo_id"].unique():
    df = fair[fair["ativo_id"] == i]
    df = df.reset_index().drop("index", 1)

    #st.dataframe(df)
    masquerede = face[
        (face["Empresa"] == "Credito")
        & (face["Categoria"] == 'Colaterizado')
        & (face["Produto"] == "Crédito XP")]
    #st.dataframe(masquerede)
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
        grasph_df["id"] = df.client_id[0]
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
        grasph_df["id"] = df.client_id[0]
    #st.dataframe(grasph_df)
    smart = smart.append(grasph_df)
smart["Mês"] = smart["Mês"].apply(lambda x: DT.datetime.strptime(x, "%b-%y"))
smart["Mês"] = smart["Mês"].apply(lambda x: DT.datetime.strftime(x, "%m-%y"))
try:
    Invest = smart[smart['PL Retido'].notna()]
    Invest = (Invest[["Mês", "Resultado assessor"]]
        .groupby(Invest["Mês"])["Resultado assessor"]
        .sum()
        .reset_index())
    Invest["Mês"] = Invest["Mês"].apply(lambda x: DT.datetime.strptime(x, "%m-%y"))
    Invest["ano"] = Invest["Mês"].astype("datetime64").dt.year
    Invest["mes"] = Invest["Mês"].astype("datetime64").dt.month
    Invest["Mês"] = Invest["Mês"].apply(lambda x: DT.datetime.strftime(x, "%b-%y"))
    Invest = Invest.sort_values(["ano", "mes"]).reset_index(drop=True)
    Invest["label"]= "InvestSmart"

except:
    Invest = pd.DataFrame(columns={
        "Mês",
        "Resultado assessor",
        "ano",
        "mes",
        "label"
    })
try:
    Besmart = smart[smart['Custo do Produto'].notna()]
    Besmart = (Besmart[["Mês", "Resultado assessor"]]
        .groupby(Besmart["Mês"])["Resultado assessor"]
        .sum()
        .reset_index())
    Besmart["Mês"] = Besmart["Mês"].apply(lambda x: DT.datetime.strptime(x, "%m-%y"))
    Besmart["ano"] = Besmart["Mês"].astype("datetime64").dt.year
    Besmart["mes"] = Besmart["Mês"].astype("datetime64").dt.month
    Besmart["Mês"] = Besmart["Mês"].apply(lambda x: DT.datetime.strftime(x, "%b-%y"))
    Besmart["label"]= "BeSmart"
except:
    Besmart = pd.DataFrame(columns={
        "Mês",
        "Resultado assessor",
        "ano",
        "mes",
        "label"
    })
try:
    super_smart = Besmart.append(Invest)
    super_smart = super_smart.sort_values(["ano", "mes"]).reset_index(drop=True)
   
except:
    super_smart = pd.DataFrame(columns={
        "Mês",
        "Resultado assessor",
        "ano",
        "mes",
        "label"
    })
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
#st.dataframe(final)
result_month = final["Resultado assessor"][(final["mes"] == DT.datetime.now().month)& (final["ano"] == DT.datetime.now().year)]
avrg_year1 = (final["Resultado assessor"][final["ano"] == DT.datetime.now().year].sum())
avrg_year2 = (final["Resultado assessor"][
    final["ano"] == DT.datetime.now().year + 1
].sum())
try:
    retorno.metric(
        "Comissão Esperada para esse mês",
        "R$ "
        + locale.currency(
            result_month.iloc[0],
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
    f"Comissão Esperada de {DT.datetime.now().year}",
    "R$ "
    + locale.currency(
        avrg_year1,
        grouping=True,
        symbol=None,
    )[:-3],
)

ano2_avg.metric(
    f"Comissão Esperada de {DT.datetime.now().year+1}",
    "R$ "
    + locale.currency(
        avrg_year2,
        grouping=True,
        symbol=None,
    )[:-3],
)



#######################################################################################
################################ COMISSÃO POR CLIENTE #################################
#######################################################################################
metrics = smart.copy()
metrics["Mês"] = metrics["Mês"].apply(lambda x: DT.datetime.strptime(x, "%m-%y"))
metrics["ano"] = metrics["Mês"].astype("datetime64").dt.year
metrics["mes"] = metrics["Mês"].astype("datetime64").dt.month
metrics["Mês"] = metrics["Mês"].apply(lambda x: DT.datetime.strftime(x, "%b-%y"))
metrics = metrics.sort_values(["ano", "mes"]).reset_index(drop=True)
#st.dataframe(metrics)

dark[f"Comissão esperada {DT.datetime.now().year}"] =[0 if metrics.empty else
    locale.currency(metrics[["ano", "Resultado assessor","id","mes"]][(metrics["ano"] == DT.datetime.now().year) & (metrics["id"] == i)].groupby("mes").sum()["Resultado assessor"].sum(), grouping=True) for i in dark["client_id"]
]

dark[f"Comissão esperada {DT.datetime.now().year+1}"] =[0 if metrics.empty else
   locale.currency(metrics[["ano", "Resultado assessor","id","mes"]][(metrics["ano"] == DT.datetime.now().year+1) & (metrics["id"] == i)].groupby("mes").sum()["Resultado assessor"].sum(), grouping=True) for i in dark["client_id"]
]

try:
    dark["Investimentos"] = dark["Investimentos"].apply(lambda x: x[:-3])
except:
    pass
try:
    dark[f"Comissão esperada {DT.datetime.now().year}"] = dark[f"Comissão esperada {DT.datetime.now().year}"].apply(lambda x: x[:-3])
except:
    dark[f"Comissão esperada {DT.datetime.now().year}"] = 0
try:
    dark[f"Comissão esperada {DT.datetime.now().year+1}"] = dark[f"Comissão esperada {DT.datetime.now().year+1}"].apply(lambda x: x[:-3])
except:
    
    dark[f"Comissão esperada {DT.datetime.now().year+1}"] = 0

#st.dataframe(dark)
# st.dataframe(result_month)
dark = dark.replace("R$ nan", "R$ 0")


#######################################################################################
################################# LAYOUT DO CONTEÚDO ##################################
#######################################################################################

st.markdown(
    """
    <hr style="height:1px;border:none;color:#9966ff;background-color:#9966ff;" /> 
    """,
    unsafe_allow_html=True,
)

vacuo, botao_1, botao_2, botao_3, vacuo_2 = st.columns([4,3,3,3,3])

vazio1, cliente, vazio2 = st.columns([0.1, 15, 0.1])

st.markdown(
    """
    <hr style="height:1px;border:none;color:#9966ff;background-color:#9966ff;" /> 
    """,
    unsafe_allow_html=True,
)
container = st.container()
chart1, chart2 = st.columns([6, 4])

#######################################################################################
############################### TABLES CLIENTE E ATIVOS ###############################
#######################################################################################

with cliente:
    # dark["PL Aplicado"] = dark["PL Aplicado"].apply(lambda x: "R$ " + str(x))
    htmlstr = f"<p style='background-color: #9966ff; color: #000000; font-size: 16px; border-radius: 7px; padding-left: 8px; text-align: center'>Carteira de Clientes</style></p>"
    st.markdown(htmlstr, unsafe_allow_html=True)

    gridOptions = GridOptionsBuilder.from_dataframe(
        dark[
            [
                "Nome do Cliente",
                "Data de Cadastro",
                "Investimentos",
                "Qnt. Ativos InvestSmart",
                "Qnt. Produtos BeSmart",
                f"Comissão esperada {DT.datetime.now().year}",
                f"Comissão esperada {DT.datetime.now().year+1}"
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
        #height=290,
        allow_unsafe_jscode=True,
        theme=AgGridTheme.ALPINE,
        fit_columns_on_grid_load =True,
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

today = DT.datetime.strftime(DT.datetime.today(), "%Y-%m-%d")
hoje = today

with botao_1:
    if "button1" not in st.session_state:
        st.session_state["button1"] = False

    if st.button("Cadastrar um Cliente"):
        st.session_state["button1"] = not st.session_state["button1"]

    if st.session_state["button1"]:
        disco = st.text_input("Nome do Cliente: ", value="")
        if st.button("Salvar"):
            
            url = "https://"+st.secrets.domain+"rest/"+st.secrets.bignumber+"/"+st.secrets.cod_shhh+"/crm.deal.add.json?fields["+st.secrets.VAR1+f"]={id_v1}&fields["+st.secrets.VAR2+f"]={disco}&fields["+st.secrets.VAR3+f"]={today}&fields["+st.secrets.category+"]="+st.secrets.courier
            payload = {}
            headers = {
            'Cookie': 'BITRIX_SM_SALE_UID=0; qmb=0.'
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            st.success("O cliente foi adicionado ao banco de dados")
            
            st._rerun()

with botao_3:
    if "button42" not in st.session_state:
        st.session_state["button42"] = False

    if st.button("Deletar um Portifólio"):
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
                    url = "https://"+st.secrets.domain+"rest/"+st.secrets.bignumber+"/"+st.secrets.cod_shhh+"/crm.deal.delete?["+st.secrets.id+f"]={v2_client}"
                    payload = {}
                    headers = {
                    'Cookie': 'BITRIX_SM_SALE_UID=0'
                    }
                    response = requests.request("POST", url, headers=headers, data=payload)
                
                    st.success("O cliente foi deletado com sucesso")
                    tm.sleep(1)
                    st._rerun()
        with nao:
            if st.button("Não"):
                st.session_state["button42"] = False

with botao_2:
    if st.button("Visualizar o Portifólio"):
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
    <style>
        div[data-testid="stSidebarNav"] {display: none;}
        footer {visibility: hidden;}
        
        [data-testid="collapsedControl"] {display: none}
        footer {visibility: hidden;}

        img{
        background-color: rgb(18, 19, 18);
            }
        
    </style>
""",
    unsafe_allow_html=True,
)

# chart1, chart2 = st.columns([6, 4])
if super_smart.empty:
    st.text("")
    st.error("Assessor não tem Portifólio")
else:    
    super_smart["data"] = super_smart["Mês"].apply(lambda x: DT.datetime.strptime(x,"%b-%y"))
    super_smart["data"] = super_smart["data"].apply(lambda x: DT.datetime.strftime(x, "%Y/%m"))
    #st.dataframe(super_smart["data"].unique())

    distancia = list(super_smart["data"].unique())
    distancia_df = pd.DataFrame(distancia)
    #st.dataframe(distancia_df)
    distancia_df["ano"] = distancia_df[0].astype("datetime64").dt.year
    with container:
        try:
            i_n_v = distancia_df[distancia_df["ano"] == DT.datetime.now().year + 2].reset_index().iloc[-1]["index"]
            inc, end = st.select_slider("Período de tempo do Grafico",options = distancia,value=(distancia[0],distancia[i_n_v]))
        except:
            inc, end = st.select_slider("Período de tempo do Grafico",options = distancia,value=(distancia[0],distancia[-1]))

    with chart2:
        try:
            #st.dataframe(fair)
            df_categ = fair[fair["empresa"]=="INVESTSMART"].groupby("categoria")["pl_aplicado"].sum().reset_index()
            df_categ['label'] = df_categ["pl_aplicado"].apply(lambda x: locale.currency(x, grouping=True)[:-3])
            df_categ = df_categ.sort_values(by="pl_aplicado", ascending=False)
            #st.dataframe(df_categ)
            fig = px.bar(
                df_categ,
                x="pl_aplicado",
                y="categoria",
                #width=700,
                # height=500,
                text=df_categ.label,
                color="categoria",
                color_discrete_sequence=px.colors.sequential.Viridis,
                title="Total do Portifólio por Categoria",
            )
            fig.update_layout(
                font=dict(family="Arial", size=15, color="White"),
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
            st.plotly_chart(fig,use_container_width=True)
        except:
            st.error("Você não possui um Portifólio nesta ferramenta")
    with chart1:
        if super_smart.empty:

            st.error("Você não possui um Portifólio nesta ferramenta")
        else:
           
            try:
                fig = px.bar(
                        super_smart[(super_smart["data"]>= inc) & (super_smart["data"]<= end)],
                        x="Mês",
                        y="Resultado assessor",
                        color="label",
                        width=1000,
                        height=425,
                        text_auto='.2s',
                        title=f"Comissão Total Mensal",
                        color_discrete_sequence=px.colors.sequential.Viridis,
                        labels = {"label":"Empresa","Resultado assessor":"Comissão do Assessor (R$)"}
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
                    # xanchor="right",
                    # x=0.2
                    )
                    )
                fig.update_traces(textfont_size=12)
                fig.data[0].textfont.color = "white"
                fig.data[0].marker.color = "#9966ff"
                fig.data[1].marker.color = "#482878"
                fig.update_xaxes(showgrid=False)
                fig.update_yaxes(title=None)
                #fig.update_traces(textposition="top center")
                st.plotly_chart(fig,use_container_width=True)
            except:
                fig = px.bar(
                        super_smart[(super_smart["data"]>= inc) & (super_smart["data"]<= end)],
                        x="Mês",
                        y="Resultado assessor",
                        #color="label",
                        #width=1000,
                        height=425,
                        text_auto='.2s',
                        title=f"Comissão Total Mensal",
                        color_discrete_sequence=px.colors.sequential.Viridis,
                        labels = {"label":"Empresa","Resultado assessor":"Comissão do Assessor (R$)"}
                    )
                fig.update_layout(
                    #showlegend=False,
                    legend_title= None,
                    uniformtext_minsize=8,
                    uniformtext_mode="hide",
                    showlegend=True,
                    legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    # xanchor="right",
                    # x=0.2,
                    )
                    )
                fig.update_traces(textfont_size=12)
                fig.data[0].textfont.color = "white"
                fig.data[0].marker.color = "#482878"
                fig.data[0]['showlegend']=True
                fig['data'][0]['name']=super_smart[(super_smart["data"]>= inc) & (super_smart["data"]<= end)]['label'].iloc[0]
                #fig.data[1].marker.color = "#482878"
                fig.update_xaxes(showgrid=False)
                fig.update_yaxes(title=None)
                #fig.update_traces(textposition="top center")
                st.plotly_chart(fig,use_container_width=True)

if st.button('Logout',key='logout2'):
    st.session_state["logout"] =None
    if st.session_state["logout"]==None:
        nav_page('')
        



