"""
Servicio de Alertas de Precio
Verifica alertas activas y envía notificaciones cuando se cumplen
"""
import sys
sys.path.append('.')

import pyodbc
from config.settings import DATABASE_URL
from services.notifications import enviar_email, crear_email_alerta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def verificar_y_notificar_alertas():
    """
    Verificar alertas activas y enviar notificaciones cuando se cumplen
    """
    logger.info("🔔 Verificando alertas activas...")
    
    try:
        conn = pyodbc.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Obtener alertas que deben ser notificadas
        query = """
            SELECT 
                a.id as alerta_id,
                a.email,
                a.precio_objetivo,
                p.id as producto_id,
                p.nombre as producto_nombre,
                (SELECT TOP 1 pr.precio 
                 FROM precios pr 
                 INNER JOIN tiendas t ON pr.tienda_id = t.id
                 WHERE pr.producto_id = p.id 
                 AND pr.fecha = (SELECT MAX(fecha) FROM precios WHERE producto_id = p.id)
                 ORDER BY pr.precio ASC) as precio_min_actual,
                (SELECT TOP 1 t.nombre 
                 FROM precios pr 
                 INNER JOIN tiendas t ON pr.tienda_id = t.id
                 WHERE pr.producto_id = p.id 
                 AND pr.fecha = (SELECT MAX(fecha) FROM precios WHERE producto_id = p.id)
                 ORDER BY pr.precio ASC) as tienda_mejor_precio,
                (SELECT TOP 1 pr.url 
                 FROM precios pr 
                 WHERE pr.producto_id = p.id 
                 AND pr.fecha = (SELECT MAX(fecha) FROM precios WHERE producto_id = p.id)
                 ORDER BY pr.precio ASC) as url_producto
            FROM alertas a
            INNER JOIN productos p ON a.producto_id = p.id
            WHERE a.activa = 1 
            AND a.notificado = 0
        """
        
        cursor.execute(query)
        alertas = cursor.fetchall()
        
        logger.info(f"📋 Alertas activas encontradas: {len(alertas)}")
        
        notificadas = 0
        
        for alerta in alertas:
            alerta_id = alerta[0]
            email = alerta[1]
            precio_objetivo = float(alerta[2])
            producto_id = alerta[3]
            producto_nombre = alerta[4]
            precio_actual = float(alerta[5]) if alerta[5] else None
            tienda = alerta[6]
            url_producto = alerta[7] or ""
            
            # Verificar si se cumple la condición
            if precio_actual and precio_actual <= precio_objetivo:
                logger.info(f"✅ Alerta cumplida para: {producto_nombre} (S/ {precio_actual} <= S/ {precio_objetivo})")
                
                # Crear y enviar email
                html_email = crear_email_alerta(
                    producto_nombre,
                    precio_actual,
                    precio_objetivo,
                    tienda,
                    url_producto
                )
                
                asunto = f"¡Alerta de Precio! {producto_nombre} ahora a S/ {precio_actual}"
                
                if enviar_email(email, asunto, html_email):
                    # Marcar alerta como notificada
                    cursor.execute("""
                        UPDATE alertas 
                        SET notificado = 1, fecha_notificacion = GETDATE()
                        WHERE id = ?
                    """, alerta_id)
                    
                    notificadas += 1
                    
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"📧 Notificaciones enviadas: {notificadas}")
        return notificadas
        
    except Exception as e:
        logger.error(f"❌ Error verificando alertas: {e}")
        return 0


if __name__ == "__main__":
    verificar_y_notificar_alertas()
