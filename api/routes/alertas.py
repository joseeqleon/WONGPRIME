"""
Rutas de Alertas
"""
from fastapi import APIRouter, HTTPException
from typing import List
from api.schemas.schemas import AlertaCreate, AlertaResponse, MessageResponse
from api.database import execute_query

router = APIRouter(prefix="/alertas", tags=["Alertas"])


@router.get("/", response_model=List[AlertaResponse])
async def get_alertas(email: str = None):
    """Obtener alertas (opcionalmente filtradas por email)"""
    
    query = "SELECT * FROM alertas WHERE 1=1"
    params = []
    
    if email:
        query += " AND email = ?"
        params.append(email)
        
    query += " ORDER BY fecha_creacion DESC"
    
    alertas = execute_query(query, params if params else None, fetchall=True)
    return alertas


@router.post("/", response_model=AlertaResponse)
async def create_alerta(alerta: AlertaCreate):
    """Crear nueva alerta de precio"""
    
    # Verificar que el producto existe
    producto_query = "SELECT id FROM productos WHERE id = ?"
    producto = execute_query(producto_query, [alerta.producto_id], fetchone=True)
    
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
        
    # Crear alerta
    query = """
        INSERT INTO alertas (producto_id, email, precio_objetivo)
        OUTPUT INSERTED.*
        VALUES (?, ?, ?)
    """
    
    from api.database import get_db_connection, row_to_dict
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(query, [alerta.producto_id, alerta.email, alerta.precio_objetivo])
        nueva_alerta = row_to_dict(cursor.fetchone(), cursor)
        conn.commit()
        return nueva_alerta
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.delete("/{alerta_id}", response_model=MessageResponse)
async def delete_alerta(alerta_id: int):
    """Eliminar una alerta"""
    
    query = "DELETE FROM alertas WHERE id = ?"
    rows_affected = execute_query(query, [alerta_id])
    
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
        
    return MessageResponse(message="Alerta eliminada correctamente")


@router.put("/{alerta_id}/desactivar", response_model=MessageResponse)
async def desactivar_alerta(alerta_id: int):
    """Desactivar una alerta"""
    
    query = "UPDATE alertas SET activa = 0 WHERE id = ?"
    rows_affected = execute_query(query, [alerta_id])
    
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
        
    return MessageResponse(message="Alerta desactivada correctamente")
