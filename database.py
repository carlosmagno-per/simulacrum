import locale
import numpy 
import pandas as pd
import datetime as DT
import math
import os
import requests
import streamlit as st


def moeda(df, colunas: list):
    """

    Esta função transforma os valores das colunas em uma string seguindo a moeda local Brasileira.

    df:Recebe um Data Frame;
    colunas: Recebe uma lista com o nome das colunas que serão alteradas.

    """
    locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
    try:
        for i in colunas:
            df[i] = df[i].astype(float)
            df[i] = "R$ " + df.apply(
                lambda x: locale.currency(x[i], grouping=True, symbol=None), axis=1
            )
        return df
    except:
        print(f"A COLUNA {i} APRESENTA ALGUM ERRO")


def base_df(
    data, data_incial, pl_apl, retorno, roa_head, roa_rec, roa_reps, moeda_real=True
):
    dias = DT.datetime.strptime(str(data), "%Y-%m-%d") - DT.datetime.strptime(
        str(data_incial), "%Y-%m-%d"
    )
    mes = round(dias.days / 30)

    endDate = DT.datetime.strptime(str(data), "%Y-%m-%d")
    startDate = DT.datetime.strptime(str(data_incial), "%Y-%m-%d")

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

    if moeda_real:
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

        dataframe["Roa/Mês(%)"] = dataframe["Roa/Mês(%)"].apply(
            lambda x: "{:,.2f}%".format(x)
        )
        return dataframe
    else:
        return dataframe


def besmart_base(
    data, data_inicial, face, empresa, categoria, produto, pl_apl, roa_reps, roa_rec=0,impost=0.2, corretag=0
):

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
    df["Corretagem"] = df["Custo do Produto"]*corretag
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
    if df["Corretagem"].iloc[0] != 0:
        df["Corretagem Bruta"] = 0
        df["Corretagem Bruta"].iloc[0] = corretag*100
        df["Resultado Bruto"] = df["Corretagem"] 
        df["Imposto"] = df["Resultado Bruto"] * impost
        df["Corretagem Líquida"] = df["Resultado Bruto"] - df["Imposto"]
        df["Resultado assessor"] = (df["Comissão Bruta"] / 100) * df["Corretagem Líquida"]
        df["Comissão Bruta"] = df["Comissão Bruta"].apply(
            lambda x: "{:,.2f}%".format(x)
        )
        df["Corretagem Bruta"] = df["Corretagem Bruta"].apply(
            lambda x: "{:,.2f}%".format(x)
        )
    else:
        df["Resultado Bruto"] = (df["Comissão Bruta"] / 100) * df["Custo do Produto"]
    
        df["Imposto"] = df["Resultado Bruto"] * impost
        
        df["Receita Líquida"] = df["Resultado Bruto"] - df["Imposto"]
        df["Resultado assessor"] = df["Receita Líquida"] * (roa_reps / 100)

        df["Comissão Bruta"] = df["Comissão Bruta"].apply(
            lambda x: "{:,.2f}%".format(x)
        )
    return df

class PositivadorBitrix:

    def __init__(self):

        self.base_url = "https://" + st.secrets.domain

        self.relative_path = st.secrets.relative_path

        self.endpoint = self.base_url + self.relative_path

 

        self.start_date = (DT.datetime.now() - DT.timedelta(days=365)).strftime("%Y-%m-%d")

        self.end_date = DT.datetime.now().strftime("%Y-%m-%d")

 

    def get_data_default(self,categ_id: int):

        query_params = {"table": "crm_deal"}

 

        request_body = {

            "dateRange": {"startDate": "2021-01-01", "endDate": self.end_date},

            "key": st.secrets.key,

            "fields": [

                {"name": st.secrets.title},

                {"name": st.secrets.id},

                {"name": st.secrets.oportunidade},

                {"name": st.secrets.contato},

                {"name": st.secrets.assigned},

            ],

            "dimensionsFilters": [

                [

                    {

                        "fieldName": st.secrets.category,

                        "values": [categ_id],

                        "type": "INCLUDE",

                        "operator": "EQUALS",

                    }

                ]

            ],

        }

 

        headers = {"Content-Type": "application/json"}

 

        response = requests.post(

            self.endpoint, headers=headers, params=query_params, json=request_body

        )

 

        df = response.json()

 

        return pd.DataFrame(df[1:], columns=df[0])

 

    def get_data_custom(self, list_id: list):

        query_params = {"table": "crm_deal_uf"}

 

        request_body = {

            "dateRange": {"startDate": "2021-01-01", "endDate": self.end_date},

            "key": st.secrets.key,

            "fields": [


                {"name": st.secrets.VAR1}, # "SIGLA_ASSESSOR" METODO DE IDENTIFICAÇÃO DO ASSESSOR OU PESSOA USANDO O SIMULADOR

                {"name": st.secrets.VAR2},  # "NOME_CLIENTE" COLOCADO NO SIMULADOR

                {"name": st.secrets.VAR3},  # "DATA_ENTRADA_CLIENTE"

                {"name": st.secrets.deal},
                

            ],

            "dimensionsFilters": [

                [

                    {

                        "fieldName": st.secrets.deal,

                        "values": list_id,

                        "type": "INCLUDE",

                        "operator": "EQUALS",

                    }

                ]

            ],
            
            

        }

 

        headers = {"Content-Type": "application/json"}

 

        response = requests.post(

            self.endpoint, headers=headers, params=query_params, json=request_body

        )

 

        df = response.json()

 

        #return print(response.text)
        return pd.DataFrame(df[1:], columns=df[0])
    
    def get_data_produto(self, id_client: int):

        query_params = {"table": "crm_deal_uf"}

 

        request_body = {

            "dateRange": {"startDate": "2021-01-01", "endDate": self.end_date},

            "key": st.secrets.key,

            "fields": [


                {"name": st.secrets.VAR11}, # "ID_CLIENTE" IDENTIFICAR O CLIENTE

                {"name": st.secrets.VAR12},  # "EMPRESA" 

                {"name": st.secrets.VAR4},  # "CATEGORIA"
                
                {"name": st.secrets.VAR5},  # "ATIVO"
                
                {"name": st.secrets.VAR10},  # "DATA_VENC"
                
                {"name": st.secrets.VAR9},  # "DATA_ATIVO"
                
                {"name": st.secrets.VAR8},  # "PL_APLICADO"
                
                {"name": st.secrets.VAR13},  # "RETORNO"
                
                {"name": st.secrets.VAR14},  # "REPASSE"
                
                {"name": st.secrets.VAR6},  # "ROA_HEAD"
                
                {"name": st.secrets.VAR7},  # "ROA_REC"

                {"name": st.secrets.deal},
                
            ],

            "dimensionsFilters": [

                [

                    {

                        "fieldName": st.secrets.VAR11,

                        "values": id_client,

                        "type": "INCLUDE",

                        "operator": "EQUALS",

                    }

                ]

            ],
            
            

        }

 

        headers = {"Content-Type": "application/json"}

 

        response = requests.post(

            self.endpoint, headers=headers, params=query_params, json=request_body

        )

 

        df = response.json()

 

        #return print(response.text)
        return pd.DataFrame(df[1:], columns=df[0])
    
    def get_data_all(self):

        query_params = {"table": "crm_deal_uf"}

 

        request_body = {

            "dateRange": {"startDate": "2021-01-01", "endDate": self.end_date},

            "key": st.secrets.key,

            "fields": [


                {"name": st.secrets.VAR11}, # "ID_CLIENTE" IDENTIFICAR O CLIENTE

                {"name": st.secrets.VAR12},  # "EMPRESA" 

                {"name": st.secrets.VAR4},  # "CATEGORIA"
                
                {"name": st.secrets.VAR5},  # "ATIVO"
                
                {"name": st.secrets.VAR10},  # "DATA_VENC"
                
                {"name": st.secrets.VAR9},  # "DATA_ATIVO"
                
                {"name": st.secrets.VAR8},  # "PL_APLICADO"
                
                {"name": st.secrets.VAR13},  # "RETORNO"
                
                {"name": st.secrets.VAR14},  # "REPASSE"
                
                {"name": st.secrets.VAR6},  # "ROA_HEAD"
                
                {"name": st.secrets.VAR7},  # "ROA_REC"

                {"name": st.secrets.deal},

            ],

        }

 

        headers = {"Content-Type": "application/json"}

 

        response = requests.post(

            self.endpoint, headers=headers, params=query_params, json=request_body

        )

 

        df = response.json()

 

        #return print(response.text)
        return pd.DataFrame(df[1:], columns=df[0])
    
    
    def get_data_repasse(self, id_client):

        query_params = {"table": "crm_deal_uf"}

 

        request_body = {

            "dateRange": {"startDate": "2021-01-01", "endDate": self.end_date},

            "key": st.secrets.key,

            "fields": [


                {"name": st.secrets.VAR15}, # "ID_EMAIL" 

                {"name": st.secrets.VAR16},  # "REPASSE INVESTSMART" 

                {"name": st.secrets.VAR17},  # "REPASSE SEGUROS"
                
                {"name": st.secrets.VAR18},  # "REPASSE CAMBIO"
                
                {"name": st.secrets.VAR19},  # "REPASSE CREDITO"
                
                {"name": st.secrets.VAR20},  # "REPASSE IMOVEL"

                {"name": st.secrets.deal},
                
            ],

            "dimensionsFilters": [

                [

                    {

                        "fieldName": st.secrets.VAR15,

                        "values": id_client,

                        "type": "INCLUDE",

                        "operator": "EQUALS",

                    }

                ]

            ],
            
            

        }

 

        headers = {"Content-Type": "application/json"}

 

        response = requests.post(

            self.endpoint, headers=headers, params=query_params, json=request_body

        )

 

        df = response.json()

 

        #return print(response.text)
        return pd.DataFrame(df[1:], columns=df[0])