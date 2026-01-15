"""
Rutas de Estadísticas y Datos Generales
"""
from fastapi import APIRouter
from typing import List
from api.schemas.schemas import EstadisticasResponse
from api.database import execute_query

router = APIRouter(prefix="/estadisticas", tags=["Estadísticas"])


@router.get("/", response_model=EstadisticasResponse)
async def get_estadisticas():
    """Obtener estadísticas generales del sistema"""
    
    # Total productos
    total_productos = execute_query("SELECT COUNT(*) FROM productos")[0]
    
    # Total tiendas
    total_tiendas = execute_query("SELECT COUNT(*) FROM tiendas WHERE activo = 1")[0]
    
    # Total categorías
    total_categorias = execute_query("SELECT COUNT(*) FROM categorias WHERE activo = 1")[0]
    
    # Total alertas activas
    total_alertas = execute_query("SELECT COUNT(*) FROM alertas WHERE activa = 1")[0]
    
    # Último scraping
    ultimo_scraping_row = execute_query(
        "SELECT MAX(fecha) FROM scraping_logs", 
        fetchone=True
    )
    ultimo_scraping = ultimo_scraping_row[0] if ultimo_scraping_row and ultimo_scraping_row[0] else None
    
    # Productos por tienda
    productos_tienda = execute_query("""
        SELECT t.nombre, COUNT(DISTINCT pr.producto_id) as total
        FROM tiendas t
        LEFT JOIN precios pr ON t.id = pr.tienda_id
        GROUP BY t.nombre
    """, fetchall=True)
    
    productos_por_tienda = {item['nombre']: item['total'] for item in productos_tienda}
    
    # Productos por categoría
    productos_cat = execute_query("""
        SELECT c.nombre, COUNT(p.id) as total
        FROM categorias c
        LEFT JOIN productos p ON c.id = p.categoria_id
        GROUP BY c.nombre
    """, fetchall=True)
    
    productos_por_categoria = {item['nombre']: item['total'] for item in productos_cat}
    
    return EstadisticasResponse(
        total_productos=total_productos,
        total_tiendas=total_tiendas,
        total_categorias=total_categorias,
        total_alertas_activas=total_alertas,
        ultimo_scraping=ultimo_scraping,
        productos_por_tienda=productos_por_tienda,
        productos_por_categoria=productos_por_categoria
    )


@router.get("/categorias")
async def get_categorias():
    """Obtener lista de categorías"""
    return execute_query("SELECT * FROM categorias WHERE activo = 1", fetchall=True)


@router.get("/marcas")
async def get_marcas():
    """Obtener lista de marcas"""
    return execute_query("SELECT * FROM marcas ORDER BY nombre", fetchall=True)


@router.get("/tiendas")
async def get_tiendas():
    """Obtener lista de tiendas"""
    return execute_query("SELECT * FROM tiendas WHERE activo = 1", fetchall=True)
