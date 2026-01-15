"""
Servicio de Generación de Reportes
"""
import sys
sys.path.append('.')

import pandas as pd
import pyodbc
from config.settings import DATABASE_URL
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generar_reporte_excel(archivo_salida="reporte_productos.xlsx"):
    """
    Generar reporte Excel con productos y precios
    """
    logger.info(f"📊 Generando reporte Excel: {archivo_salida}")
    
    try:
        conn = pyodbc.connect(DATABASE_URL)
        
        # Query para obtener datos
        query = """
            SELECT 
                p.nombre as Producto,
                m.nombre as Marca,
                c.nombre as Categoria,
                t.nombre as Tienda,
                pr.precio as Precio,
                pr.stock as Stock,
                pr.rating as Rating,
                pr.fecha as Fecha_Actualizacion
            FROM productos p
            LEFT JOIN marcas m ON p.marca_id = m.id
            LEFT JOIN categorias c ON p.categoria_id = c.id
            INNER JOIN precios pr ON p.id = pr.producto_id
            INNER JOIN tiendas t ON pr.tienda_id = t.id
            WHERE pr.fecha = (
                SELECT MAX(fecha) 
                FROM precios 
                WHERE producto_id = p.id AND tienda_id = pr.tienda_id
            )
            ORDER BY p.nombre, t.nombre
        """
        
        # Cargar datos en DataFrame
        df = pd.read_sql(query, conn)
        
        # Crear Excel con múltiples hojas
        with pd.ExcelWriter(archivo_salida, engine='openpyxl') as writer:
            # Hoja 1: Todos los productos
            df.to_excel(writer, sheet_name='Productos', index=False)
            
            # Hoja 2: Comparación por producto
            pivot = df.pivot_table(
                values='Precio',
                index=['Producto', 'Marca', 'Categoria'],
                columns='Tienda',
                aggfunc='min'
            )
            pivot.to_excel(writer, sheet_name='Comparacion')
            
            # Hoja 3: Estadísticas
            stats_query = """
                SELECT 
                    'Total Productos' as Metrica, COUNT(*) as Valor FROM productos
                UNION ALL
                SELECT 'Total Tiendas', COUNT(*) FROM tiendas WHERE activo = 1
                UNION ALL
                SELECT 'Total Categorias', COUNT(*) FROM categorias WHERE activo = 1
                UNION ALL
                SELECT 'Alertas Activas', COUNT(*) FROM alertas WHERE activa = 1
            """
            stats_df = pd.read_sql(stats_query, conn)
            stats_df.to_excel(writer, sheet_name='Estadisticas', index=False)
            
        conn.close()
        
        logger.info(f"✅ Reporte generado: {archivo_salida}")
        return archivo_salida
        
    except Exception as e:
        logger.error(f"❌ Error generando reporte: {e}")
        return None


def generar_reporte_comparacion(categoria=None, archivo_salida="comparacion_precios.xlsx"):
    """
    Generar reporte de comparación de precios entre tiendas
    """
    logger.info(f"📊 Generando reporte de comparación...")
    
    try:
        conn = pyodbc.connect(DATABASE_URL)
        
        query = "SELECT * FROM vw_comparacion_tiendas"
        params = None
        
        if categoria:
            query += " WHERE categoria LIKE ?"
            params = [f"%{categoria}%"]
            
        df = pd.read_sql(query, conn, params=params)
        
        # Calcular ahorro potencial
        df['mejor_precio'] = df[['precio_wong', 'precio_metro', 'precio_plaza_vea']].min(axis=1)
        df['peor_precio'] = df[['precio_wong', 'precio_metro', 'precio_plaza_vea']].max(axis=1)
        df['ahorro_potencial'] = df['peor_precio'] - df['mejor_precio']
        
        # Determinar mejor tienda para cada producto
        def obtener_mejor_tienda(row):
            precios = {
                'Wong': row['precio_wong'],
                'Metro': row['precio_metro'],
                'Plaza Vea': row['precio_plaza_vea']
            }
            precios_validos = {k: v for k, v in precios.items() if pd.notna(v)}
            if precios_validos:
                return min(precios_validos, key=precios_validos.get)
            return None
            
        df['mejor_tienda'] = df.apply(obtener_mejor_tienda, axis=1)
        
        # Guardar
        df.to_excel(archivo_salida, index=False)
        conn.close()
        
        logger.info(f"✅ Reporte de comparación generado: {archivo_salida}")
        return archivo_salida
        
    except Exception as e:
        logger.error(f"❌ Error generando reporte: {e}")
        return None


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generar reportes de WongPrime')
    parser.add_argument('--format', choices=['excel', 'comparacion'], default='excel',
                       help='Tipo de reporte a generar')
    parser.add_argument('--output', default=None, help='Archivo de salida')
    parser.add_argument('--categoria', default=None, help='Filtrar por categoría')
    
    args = parser.parse_args()
    
    if args.format == 'excel':
        output = args.output or "reporte_productos.xlsx"
        generar_reporte_excel(output)
    elif args.format == 'comparacion':
        output = args.output or "comparacion_precios.xlsx"
        generar_reporte_comparacion(args.categoria, output)
