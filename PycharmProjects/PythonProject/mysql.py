
import pymysql

# 打开数据库连接
db = pymysql.connect(host='10.69.66.75',
                     port=8983,
                     user='root',
                     password='admin',
                     database='yichang_test')

# 使用 cursor() 方法创建一个游标对象 cursor
cursor = db.cursor()

# 使用 execute()  方法执行 SQL 查询
cursor.execute("show tables")

# 使用 fetchone() 方法获取单条数据.
results = cursor.fetchall()

try:
    for row in results:
        print(row[0])
except Exception as e:
    print(e)
finally:
    # 关闭数据库连接
    db.close()