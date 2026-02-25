
from sqlalchemy import create_engine, text

mysql_user = 'root'
mysql_pass = '8Dm4PQU2pp6!C3y'
mysql_url = 'rm-bp160jkc22y874i30to.mysql.rds.aliyuncs.com:3306'
mysql_db = 'stock'

def getDbEngine():
    return create_engine('mysql+pymysql://' + mysql_user + ':' + mysql_pass + '@' + mysql_url + '/' + mysql_db)
