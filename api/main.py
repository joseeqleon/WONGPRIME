"""
WongPrime API - FastAPI Application
"""
import sys
sys.path.append('.')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from api.routes import productos, alertas, estadisticas
from config.settings import API_HOST, API_PORT, API_RELOAD

# Crear aplicación FastAPI
app = FastAPI(
    title="WongPrime API",
    description="API REST para comparación de precios multi-tienda",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(productos.router)
app.include_router(alertas.router)
app.include_router(estadisticas.router)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Página de bienvenida"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WongPrime API</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                background: rgba(255,255,255,0.1);
                padding: 40px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
            }
            h1 {
                font-size: 3em;
                margin: 0;
            }
            p {
                font-size: 1.2em;
                margin: 20px 0;
            }
            a {
                display: inline-block;
                margin: 10px 10px 10px 0;
                padding: 12px 24px;
                background: white;
                color: #667eea;
                text-decoration: none;
                border-radius: 8px;
                font-weight: bold;
                transition: transform 0.2s;
            }
            a:hover {
                transform: translateY(-2px);
            }
            .features {
                margin-top: 30px;
            }
            .feature {
                background: rgba(255,255,255,0.1);
                padding: 15px;
                margin: 10px 0;
                border-radius: 8px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛒 WongPrime API</h1>
            <p>API REST para comparación de precios multi-tienda</p>
            
            <div>
                <a href="/docs">📚 Documentación (Swagger)</a>
                <a href="/redoc">📖 Documentación (ReDoc)</a>
            </div>
            
            <div class="features">
                <h2>✨ Características</h2>
                <div class="feature">📦 Consulta de productos con filtros</div>
                <div class="feature">📊 Histórico de precios</div>
                <div class="feature">🏪 Comparación entre tiendas</div>
                <div class="feature">🔔 Sistema de alertas de precio</div>
                <div class="feature">📈 Estadísticas generales</div>
            </div>
        </div>
    </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "WongPrime API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=API_RELOAD
    )
