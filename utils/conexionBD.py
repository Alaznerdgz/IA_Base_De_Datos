import pyodbc

# Información de conexión
server = 'A407PC23\\SQLEXPRESS'
database = 'Pubs'
username = 'sa'
password = 'tiger'
driver = '{ODBC Driver 17 for SQL Server}'
conn = None
def getConexion():
        if conn != None:
            return conn
        else:
            # Crear la cadena de conexión
            conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
            
            # Establecer la conexión
            conn = pyodbc.connect(conn_str)
            return conn