from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
import pyodbc
from datetime import datetime
import time
import sys
import os
import io
import logging

# =============================
# ENCODING WINDOWS
# =============================
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# =============================
# LOGGING
# =============================
logging.basicConfig(
    filename="scraping_wong.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# =============================
# CONFIGURACIÓN
# =============================
URL_WONG = "https://www.wong.pe/higiene-salud-y-belleza/salud"

CHROMEDRIVER_PATH = r"C:\scraping_wong\chromedriver.exe"
BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

# =============================
# CONEXIÓN A SQL SERVER
# =============================
try:
    print("🔌 Conectando a SQL Server...")
    conn = pyodbc.connect(
        "DRIVER={SQL Server};"
        "SERVER=LP\\SQLEXPRESS;"
        "DATABASE=ScrapingWong;"
        "Trusted_Connection=yes;"
    )
    cursor = conn.cursor()
    print("✅ Conexión exitosa a SQL Server")
    logging.info("Conectado a SQL Server")
except Exception as e:
    logging.error(f"Error conexión BD: {e}")
    print("❌ Error al conectar a SQL Server")
    sys.exit()

# =============================
# SELENIUM (AUTO NAVEGADOR)
# =============================
driver = None
try:
    print("🌐 Iniciando navegador...")

    options = Options()
    options.add_argument("--start-maximized")

    if os.path.exists(BRAVE_PATH):
        options.binary_location = BRAVE_PATH
        print("➡️ Usando Brave")
    else:
        print("➡️ Usando Chrome")

    if os.path.exists(CHROMEDRIVER_PATH):
        service = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
    else:
        driver = webdriver.Chrome(options=options)

    driver.get(URL_WONG)
    time.sleep(8)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    productos = soup.select("div.product-item")

    print(f"📦 Productos encontrados: {len(productos)}")
    logging.info(f"{len(productos)} productos detectados")

    contador = 0

    for producto in productos:
        nombre = producto.select_one("p.product-title")
        precio = producto.select_one("span.product-prices__value")

        if nombre and precio:
            nombre_txt = nombre.text.strip()
            precio_txt = precio.text.replace("S/", "").replace(",", "").strip()

            try:
                precio_num = float(precio_txt)

                cursor.execute("""
                    INSERT INTO productos_wong
                    (nombre, precio, categoria, url, fecha_extraccion)
                    VALUES (?, ?, ?, ?, ?)
                """,
                nombre_txt,
                precio_num,
                "Salud",
                URL_WONG,
                datetime.now()
                )

                contador += 1

            except ValueError:
                logging.warning(f"Precio inválido: {precio_txt}")
                print(f"⚠️ Precio inválido: {precio_txt}")

    conn.commit()
    print(f"✅ {contador} productos insertados en la base de datos")
    logging.info(f"{contador} productos insertados")

except WebDriverException as e:
    logging.error(f"Error Selenium: {e}")
    print("❌ Error al iniciar el navegador")

except Exception as e:
    logging.error(f"Error scraping: {e}")
    print("❌ Error durante el scraping")

finally:
    if driver:
        driver.quit()
        print("🧹 Navegador cerrado")
    if conn:
        conn.close()
        print("🔒 Conexión a SQL Server cerrada")
