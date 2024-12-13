



import tushare as ts
from sqlalchemy import create_engine

ts.set_token('3252a9af155128787f44d053c563d6b156f03e80f0254899e8668ecc')

pro = ts.pro_api()

data = pro.stock_basic(exchange='', list_status='L')

data.to_csv('stock.csv')

engine = create_engine('mysql+pymysql://wgx_mysql:8Dm4PQU2pp6!C3y@rm-bp1eqw5j01245gr6jao.mysql.rds.aliyuncs.com:3306/stock')

data.to_sql('stock', con=engine, if_exists='replace', index=False)