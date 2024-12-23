import adbc_driver_flightsql
import adbc_driver_manager
import adbc_driver_flightsql.dbapi as flight_sql

import pyarrow as pa


def flight_sql():

    print(adbc_driver_manager.__version__)
    print(adbc_driver_flightsql.__version__)

    conn = flight_sql.connect(uri="grpc://10.69.66.75:8811", db_kwargs={
                adbc_driver_manager.DatabaseOptions.USERNAME.value: "root",
                adbc_driver_manager.DatabaseOptions.PASSWORD.value: "admin",
            })
    cursor = conn.cursor()

    cursor.execute("show databases")

    print(cursor.fetchallarrow())

    cursor.execute("select * from tpch.orders limit 100")

    pd = cursor.fetchallarrow().to_pandas()

    print(pd.to_string(index=False))

def pyarrow_sql():
    import pyarrow as pa
    import pyarrow.parquet as pq
    # import pyarrow.doris as doris
    #
    # # 替换为您的Doris集群信息
    # doris_host = "10.69.66.75"
    # doris_port = 8978
    # doris_user = "root"
    # doris_passwd = "admin"
    # doris_database = "tpch"
    # doris_table = "your_table"
    #
    # # 创建Doris连接
    # doris_conn_str = f"http://{doris_user}:{doris_passwd}@{doris_host}:{doris_port}"
    #
    # pa.table()
    # # 读取Doris表数据
    # table = pa.table({
    #     'column_name1': [...],  # 替换为实际数据
    #     'column_name2': [...],  # 替换为实际数据
    #     ...
    # })
    #
    # # 将PyArrow表保存为Parquet文件
    # pq.write_table(table, "output.parquet")
    pass

if __name__ == '__main__':
    pyarrow_sql()