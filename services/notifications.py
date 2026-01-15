"""
Servicio de Notificaciones por Email
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
sys.path.append('.')

from config.settings import SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, EMAIL_FROM
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def enviar_email(destinatario, asunto, cuerpo_html):
    """
    Enviar email usando SMTP
    
    Args:
        destinatario: Email del destinatario
        asunto: Asunto del email
        cuerpo_html: Contenido HTML del email
    """
    
    if not SMTP_USER or not SMTP_PASSWORD:
        logger.warning("Credenciales SMTP no configuradas. Email no enviado.")
        return False
        
    try:
        # Crear mensaje
        mensaje = MIMEMultipart('alternative')
        mensaje['Subject'] = asunto
        mensaje['From'] = EMAIL_FROM
        mensaje['To'] = destinatario
        
        # Agregar cuerpo HTML
        parte_html = MIMEText(cuerpo_html, 'html')
        mensaje.attach(parte_html)
        
        # Conectar y enviar
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(mensaje)
            
        logger.info(f"✅ Email enviado a {destinatario}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error enviando email: {e}")
        return False


def crear_email_alerta(producto_nombre, precio_actual, precio_objetivo, tienda, url_producto):
    """Crear HTML para email de alerta de precio"""
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f9f9f9;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
                border-radius: 10px 10px 0 0;
            }}
            .content {{
                background: white;
                padding: 30px;
                border-radius: 0 0 10px 10px;
            }}
            .price-box {{
                background: #e8f5e9;
                border-left: 4px solid #4caf50;
                padding: 15px;
                margin: 20px 0;
            }}
            .price {{
                font-size: 2em;
                color: #4caf50;
                font-weight: bold;
            }}
            .button {{
                display: inline-block;
                padding: 12px 30px;
                background: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 ¡Alerta de Precio!</h1>
            </div>
            <div class="content">
                <h2>¡El precio bajó!</h2>
                <p>El producto que estás siguiendo ha alcanzado tu precio objetivo:</p>
                
                <h3>{producto_nombre}</h3>
                
                <div class="price-box">
                    <p><strong>Precio actual:</strong></p>
                    <div class="price">S/ {precio_actual:.2f}</div>
                    <p><strong>Tu precio objetivo:</strong> S/ {precio_objetivo:.2f}</p>
                    <p><strong>Tienda:</strong> {tienda}</p>
                </div>
                
                <p>¡No dejes pasar esta oportunidad!</p>
                
                <a href="{url_producto}" class="button">Ver Producto</a>
                
                <p style="margin-top: 30px; color: #666; font-size: 0.9em;">
                    Este es un mensaje automático de WongPrime.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html
