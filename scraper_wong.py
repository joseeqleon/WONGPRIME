from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pyodbc
from datetime import datetime
import time
import sys
import os
import logging

# =============================
# ENCODING WINDOWS
# =============================
if sys.stdout.encoding != 'utf-8':
    import io
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
CHROMEDRIVER_PATH = r"C:\scraping_wong\chromedriver.exe"
BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
URL_WONG = "https://www.wong.pe/higiene-salud-y-belleza/salud"

# =============================
# CONEXIÓN A SQL SERVER
# =============================
try:
    logging.info("Conectando a SQL Server")
    conn = pyodbc.connect(
        "DRIVER={SQL Server};"
        "SERVER=LP\\SQLEXPRESS;"
        "DATABASE=ScrapingWong;"
        "Trusted_Connection=yes;"
    )
    cursor = conn.cursor()
    print("Conexión exitosa a SQL Server.")
except Exception as e:
    logging.error(f"Error conexión BD: {e}")
    sys.exit()

# =============================
# SELENIUM
# =============================
driver = None
try:
    options = Options()

    if os.path.exists(BRAVE_PATH):
        options.binary_location = BRAVE_PATH
        print("Usando Brave")
    else:
        print("Usando Chrome")

    options.add_argument("--start-maximized")

    if os.path.exists(CHROMEDRIVER_PATH):
        service = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
    else:
        driver = webdriver.Chrome(options=options)

    driver.get(URL_WONG)
    time.sleep(8)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    productos = soup.select("div.product-item")

    print(f"Productos encontrados: {len(productos)}")
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
                    IF NOT EXISTS (
                        SELECT 1 FROM productos_wong
                        WHERE nombre = ?
                        AND CAST(fecha_extraccion AS DATE) = CAST(GETDATE() AS DATE)
                    )
                    INSERT INTO productos_wong
                    (nombre, precio, categoria, url, fecha_extraccion)
                    VALUES (?, ?, ?, ?, ?)
                """,
                nombre_txt,
                nombre_txt,
                precio_num,
                "Salud",
                URL_WONG,
                datetime.now()
                )

                contador += 1

            except ValueError:
                logging.warning(f"Precio inválido: {precio_txt}")

    conn.commit()
    print(f"Proceso finalizado. {contador} registros insertados.")
    logging.info(f"{contador} productos insertados")

except Exception as e:
    logging.error(f"Error scraping: {e}")
    print("Error durante el scraping")

finally:
    if driver:
        driver.quit()
    if conn:
        conn.close()
