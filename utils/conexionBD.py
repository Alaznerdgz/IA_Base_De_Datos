import pyodbc # type: ignore

# Información de conexión
server = 'A407PC23\\SQLEXPRESS'
database = 'Pubs'
username = 'sa'
password = 'tiger'
driver = '{ODBC Driver 17 for SQL Server}'

try:
    # Crear la cadena de conexión
    conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    
    # Establecer la conexión
    conn = pyodbc.connect(conn_str)
    
    # Crear un cursor para ejecutar consultas
    cursor = conn.cursor()
    
    print("Conexión a SQL Server establecida con éxito.")
    
    # Aquí puedes ejecutar tus consultas SQL...
    # cursor.execute("SELECT * FROM MiTabla")
    # for row in cursor.fetchall():
    #     print(row)

    print(cursor.execute("SELECT au_id FROM authors").fetchall())

except pyodbc.Error as ex:
    sqlstate = ex.args[0]
    if sqlstate == '28000':
        print("Error de autenticación. Verifica tu usuario y contraseña.")
    else:
        print(f"Error al conectar a la base de datos: {ex}")