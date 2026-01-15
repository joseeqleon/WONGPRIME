"""
Rutas de Productos
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from api.schemas.schemas import (
    ProductoResponse, ProductoConPrecios, PrecioResponse,
    HistoricoPrecio, ComparacionTiendas
)
from api.database import execute_query
from datetime import datetime

router = APIRouter(prefix="/productos", tags=["Productos"])


@router.get("/", response_model=List[ProductoResponse])
async def get_productos(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    categoria: Optional[str] = None,
    marca: Optional[str] = None,
    buscar: Optional[str] = None
):
    """Obtener lista de productos con filtros opcionales"""
    
    query = """
        SELECT p.id, p.nombre, p.descripcion, p.url_imagen, 
               m.nombre as marca, c.nombre as categoria,
               p.fecha_creacion, p.ultima_actualizacion
        FROM productos p
        LEFT JOIN marcas m ON p.marca_id = m.id
        LEFT JOIN categorias c ON p.categoria_id = c.id
        WHERE 1=1
    """
    params = []
    
    if categoria:
        query += " AND c.nombre LIKE ?"
        params.append(f"%{categoria}%")
        
    if marca:
        query += " AND m.nombre LIKE ?"
        params.append(f"%{marca}%")
        
    if buscar:
        query += " AND p.nombre LIKE ?"
        params.append(f"%{buscar}%")
        
    query += " ORDER BY p.id DESC OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
    params.extend([skip, limit])
    
    productos = execute_query(query, params, fetchall=True)
    return productos


@router.get("/{producto_id}", response_model=ProductoConPrecios)
async def get_producto(producto_id: int):
    """Obtener detalle de un producto con precios actuales"""
    
    # Obtener producto
    query = """
        SELECT p.id, p.nombre, p.descripcion, p.url_imagen,
               m.nombre as marca, c.nombre as categoria,
               p.fecha_creacion, p.ultima_actualizacion
        FROM productos p
        LEFT JOIN marcas m ON p.marca_id = m.id
        LEFT JOIN categorias c ON p.categoria_id = c.id
        WHERE p.id = ?
    """
    
    producto = execute_query(query, [producto_id], fetchone=True)
    
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
        
    # Obtener precios actuales
    query_precios = """
        SELECT pr.id, pr.precio, t.nombre as tienda, pr.stock, pr.rating, pr.url, pr.fecha
        FROM precios pr
        INNER JOIN tiendas t ON pr.tienda_id = t.id
        WHERE pr.producto_id = ?
        AND pr.fecha = (SELECT MAX(fecha) FROM precios WHERE producto_id = ? AND tienda_id = pr.tienda_id)
    """
    
    precios = execute_query(query_precios, [producto_id, producto_id], fetchall=True)
    
    # Convertir a dict
    from api.database import row_to_dict, get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, [producto_id])
    producto_dict = row_to_dict(cursor.fetchone(), cursor)
    cursor.close()
    conn.close()
    
    producto_dict['precios_actuales'] = precios
    
    return producto_dict


@router.get("/{producto_id}/historico", response_model=List[HistoricoPrecio])
async def get_historico_precios(
    producto_id: int,
    tienda: Optional[str] = None,
    dias: int = Query(30, le=365)
):
    """Obtener histórico de precios de un producto"""
    
    query = """
        SELECT pr.fecha, pr.precio, t.nombre as tienda,
               LAG(pr.precio) OVER (PARTITION BY t.id ORDER BY pr.fecha) as precio_anterior
        FROM precios pr
        INNER JOIN tiendas t ON pr.tienda_id = t.id
        WHERE pr.producto_id = ?
        AND pr.fecha >= DATEADD(day, -?, GETDATE())
    """
    
    params = [producto_id, dias]
    
    if tienda:
        query += " AND t.nombre = ?"
        params.append(tienda)
        
    query += " ORDER BY pr.fecha DESC"
    
    historico = execute_query(query, params, fetchall=True)
    
    # Calcular variación porcentual
    for item in historico:
        if item.get('precio_anterior'):
            variacion = ((item['precio'] - item['precio_anterior']) / item['precio_anterior']) * 100
            item['variacion_porcentual'] = round(variacion, 2)
            
    return historico


@router.get("/{producto_id}/comparar", response_model=ComparacionTiendas)
async def comparar_tiendas(producto_id: int):
    """Comparar precios del producto entre tiendas"""
    
    query = """
        SELECT * FROM vw_comparacion_tiendas WHERE producto_id = ?
    """
    
    result = execute_query(query, [producto_id], fetchone=True)
    
    if not result:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
        
    # Convertir a dict y agregar mejor tienda
    from api.database import row_to_dict, get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, [producto_id])
    comparacion = row_to_dict(cursor.fetchone(), cursor)
    cursor.close()
    conn.close()
    
    # Determinar mejor tienda
    precios_tiendas = {
        'Wong': comparacion.get('precio_wong'),
        'Metro': comparacion.get('precio_metro'),
        'Plaza Vea': comparacion.get('precio_plaza_vea')
    }
    
    precios_validos = {k: v for k, v in precios_tiendas.items() if v is not None}
    
    if precios_validos:
        mejor_tienda = min(precios_validos, key=precios_validos.get)
        precio_min = precios_validos[mejor_tienda]
        precio_max = max(precios_validos.values())
        
        comparacion['mejor_tienda'] = mejor_tienda
        comparacion['ahorro_maximo'] = round(precio_max - precio_min, 2)
        
    return comparacion
