import os
from dotenv import load_dotenv

load_dotenv()

# Base de datos
DB_DRIVER = "SQL Server"
DB_SERVER = os.getenv("DB_SERVER", "localhost\\SQLEXPRESS")
DB_NAME = os.getenv("DB_NAME", "ScrapingWong")
DB_TRUSTED_CONNECTION = os.getenv("DB_TRUSTED_CONNECTION", "yes")

# Conexión string
DATABASE_URL = (
    f"DRIVER={{{DB_DRIVER}}};"
    f"SERVER={DB_SERVER};"
    f"DATABASE={DB_NAME};"
    f"Trusted_Connection={DB_TRUSTED_CONNECTION};"
)

# Scraping
SCRAPING_DELAY = int(os.getenv("SCRAPING_DELAY", "8"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
TIMEOUT = int(os.getenv("TIMEOUT", "30"))

# API
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_RELOAD = os.getenv("API_RELOAD", "True").lower() == "true"

# Email (para alertas)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", SMTP_USER)

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "wongprime.log")

# URLs de tiendas
WONG_BASE_URL = "https://www.wong.pe"
METRO_BASE_URL = "https://www.metro.pe"
PLAZA_VEA_BASE_URL = "https://www.plazavea.com.pe"

# Categorías a scrapear
CATEGORIAS = [
    "higiene-salud-y-belleza/salud",
    "higiene-salud-y-belleza/cuidado-personal",
    "bebes-y-ninos/alimentos-organicos"
]
