# WongPrime - Plataforma de Análisis de Precios Multi-Tienda

Sistema completo de scraping, análisis y comparación de precios de productos de salud en supermercados peruanos (Wong, Metro, Plaza Vea).

## 🚀 Características

- ✅ **Scraping Multi-Tienda**: Extrae productos de Wong, Metro y Plaza Vea
- 📊 **Base de Datos SQL Server**: Almacenamiento estructurado con histórico de precios
- 🔌 **API REST**: Endpoints para consulta y análisis de datos
- 💻 **Dashboard Web**: Interfaz visual para comparar precios y ver tendencias
- 🔔 **Sistema de Alertas**: Notificaciones por email cuando los precios bajan
- ⏰ **Automatización**: Scraping programado y reportes automáticos
- 📈 **Reportes**: Generación de reportes en Excel y PDF

## 📋 Requisitos

- Python 3.12+
- SQL Server (Express Edition funciona)
- Chrome/Edge (para Selenium)

## 🛠️ Instalación

1. **Clonar el repositorio**
```bash
cd WONGPRIME-main
```

2. **Instalar dependencias**
```bash
py -m pip install -r requirements.txt
```

3. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

4. **Crear base de datos**
```bash
sqlcmd -S "localhost\SQLEXPRESS" -i database/schema.sql
```

## 🎯 Uso

### Ejecutar Scrapers

```bash
# Scraper de Wong
py -m scrapers.wong

# Scraper de Metro
py -m scrapers.metro

# Scraper de Plaza Vea
py -m scrapers.plaza_vea

# Ejecutar todos
py run_all_scrapers.py
```

### Iniciar API REST

```bash
py -m api.main
```

Documentación automática en: http://localhost:8000/docs

### Abrir Dashboard

```bash
# Abrir dashboard/index.html en tu navegador
# O usar el servidor de desarrollo
py -m http.server 3000 --directory dashboard
```

Dashboard en: http://localhost:3000

### Sistema de Alertas

```bash
# Verificar y enviar alertas
py -m services.alerts
```

### Generar Reportes

```bash
# Reporte Excel
py -m services.reports --format excel

# Reporte PDF
py -m services.reports --format pdf
```

## 🗂️ Estructura del Proyecto

```
WONGPRIME-main/
├── scrapers/              # Módulos de scraping
│   ├── base_scraper.py    # Clase base
│   ├── wong.py           
│   ├── metro.py
│   └── plaza_vea.py
├── database/              # Esquemas y modelos
│   ├── schema.sql
│   └── models.py
├── api/                   # API REST FastAPI
│   ├── main.py
│   ├── routes/
│   └── schemas/
├── dashboard/             # Frontend web
│   ├── index.html
│   ├── css/
│   └── js/
├── services/              # Servicios
│   ├── alerts.py
│   ├── reports.py
│   └── notifications.py
├── tests/                 # Testing
├── config/
│   └── settings.py
└── requirements.txt
```

## 📡 API Endpoints

- `GET /productos` - Lista de productos
- `GET /productos/{id}` - Detalle de producto
- `GET /productos/{id}/historico` - Histórico de precios
- `GET /productos/{id}/comparar` - Comparar entre tiendas
- `POST /alertas` - Crear alerta de precio
- `GET /categorias` - Lista de categorías
- `GET /estadisticas` - Estadísticas generales

## 🧪 Testing

```bash
py -m pytest tests/
```

## ⏰ Automatización (Windows)

```bash
# Configurar tarea programada
setup_task.bat
```

## 📝 Licencia

MIT License

## 👤 Autor

Proyecto WongPrime - Análisis de Precios

---

**¿Necesitas ayuda?** Revisa la documentación en `/docs` o abre un issue.
