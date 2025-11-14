import pyodbc
from utils.conexionBD import get_connection

def ejecutar_consulta(consulta):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(consulta)
    resultados = cursor.fetchall()
    cursor.close()
    return resultados 