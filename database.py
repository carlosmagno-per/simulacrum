import sqlite3
import locale

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
