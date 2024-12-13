import adbc_driver_flightsql
import adbc_driver_manager
import adbc_driver_flightsql.dbapi as flight_sql


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