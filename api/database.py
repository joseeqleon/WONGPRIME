"""
Utilidades para la base de datos
"""
import pyodbc
import sys
sys.path.append('.')
from config.settings import DATABASE_URL


def get_db_connection():
    """Obtener conexión a la base de datos"""
    try:
        conn = pyodbc.connect(DATABASE_URL)
        return conn
    except Exception as e:
        raise Exception(f"Error conectando a la base de datos: {e}")


def execute_query(query, params=None, fetchone=False, fetchall=False):
    """Ejecutar query y retornar resultados"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        if fetchone:
            result = cursor.fetchone()
            return result
        elif fetchall:
            columns = [column[0] for column in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        else:
            conn.commit()
            return cursor.rowcount
            
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def row_to_dict(row, cursor):
    """Convertir fila de pyodbc a diccionario"""
    if row is None:
        return None
    columns = [column[0] for column in cursor.description]
    return dict(zip(columns, row))
