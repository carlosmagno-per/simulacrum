import pymysql


# database connection

con = pymysql.connect(
    host="sql10.freemysqlhosting.net",
    port=3306,
    user="sql10601707",
    passwd="RMmdB9Ki9b",
    database="sql10601707",
)

cursor = con.cursor()
