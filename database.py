import sqlite3
import locale
import numpy as np
import pandas as pd
import datetime as DT
import math
import numpy

con = sqlite3.connect("Simulador.db", check_same_thread=False)
cursor = con.cursor()

# cursor.execute(
#     """CREATE TABLE cliente (
#                   client_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
#                   sigla text NOT NULL,
#                   nome_client text NOT NULL,
#                   data_cliente text NOT NULL
#               )"""
# )

# cursor.execute(
#     """CREATE TABLE variaveis (
#                   client_id INTEGER NOT NULL,
#                   empresa text NOT NULL,
#                   categoria text NOT NULL,
#                   ativo text NOT NULL,
#                   data_venc text NOT NULL,
#                   pl_aplicado REAL NOT NULL,
#                   retorno REAL NOT NULL,
#                   repasse REAL NOT NULL,
#                   roa_head REAL NOT NULL,
#                   roa_rec REAL NOT NULL,
#                   data_ativo text NOT NULL,
#                   ativo_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
#                   FOREIGN KEY (client_id) REFERENCES cliente (client_id)
#                   ON DELETE CASCADE ON UPDATE NO ACTION
#               )"""
# )


def moeda(df, colunas: list):
    """

    Esta função transforma os voleres das colunas em uma string seguindo a moeda local Brasileira.

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
    data, data_inicial, face, empresa, categoria, produto, pl_apl, roa_reps, roa_rec=0
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
        df["Resultado Bruto"] = (df["Comissão Bruta"] / 100) * df["Custo do Produto"]
        df["Imposto"] = df["Resultado Bruto"] * 0.2
        df["Receita Líquida"] = df["Resultado Bruto"] - df["Imposto"]
        df["Resultado assessor"] = df["Receita Líquida"] * (roa_reps / 100)

        df["Comissão Bruta"] = df["Comissão Bruta"].apply(
            lambda x: "{:,.2f}%".format(x)
        )
        return df
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
        df["Resultado Bruto"] = (df["Comissão Bruta"] / 100) * df["Custo do Produto"]
        df["Imposto"] = df["Resultado Bruto"] * 0.2
        df["Receita Líquida"] = df["Resultado Bruto"] - df["Imposto"]
        df["Resultado assessor"] = df["Receita Líquida"] * (roa_reps / 100)

        df["Comissão Bruta"] = df["Comissão Bruta"].apply(
            lambda x: "{:,.2f}%".format(x)
        )
        return df
