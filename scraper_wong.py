from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
import pyodbc
from datetime import datetime
import time
import sys
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

logging.info("===== INICIO DEL SCRAPING =====")

# =============================
# CONFIGURACIÓN
# =============================
URL_WONG = "https://www.wong.pe/higiene-salud-y-belleza/salud"

# =============================
# CONEXIÓN A SQL SERVER
# =============================
try:
    print("🔌 Conectando a SQL Server...")
    conn = pyodbc.connect(
        "DRIVER={SQL Server};"
<<<<<<< HEAD
        "SERVER=localhost\\SQLEXPRESS;"
=======
        "SERVER=LP\\SQLEXPRESS;"
>>>>>>> 6e55e524704f405b1fd33acfbf892f8362ac9725
        "DATABASE=ScrapingWong;"
        "Trusted_Connection=yes;"
    )
    cursor = conn.cursor()
    print("✅ Conexion exitosa a SQL Server")
    logging.info("Conexion exitosa a SQL Server")
except Exception as e:
    print("❌ Error al conectar a SQL Server")
    logging.error(f"Error conexión SQL Server: {e}")
    sys.exit()

# =============================
# SELENIUM (AUTO NAVEGADOR)
# =============================
driver = None
try:
    print("🌐 Iniciando navegador automáticamente...")

    options = Options()
    options.add_argument("--start-maximized")

    # Selenium Manager decide navegador + driver
    driver = webdriver.Chrome(options=options)

    driver.get(URL_WONG)
    time.sleep(8)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    productos = soup.select("div.product-item")

    print(f"📦 Productos encontrados: {len(productos)}")
    logging.info(f"Productos encontrados: {len(productos)}")

    contador = 0
    duplicados = 0

    for producto in productos:
        nombre = producto.select_one("p.product-title")
        precio = producto.select_one("span.product-prices__value")

        if nombre and precio:
            nombre_txt = nombre.text.strip()
            precio_txt = precio.text.replace("S/", "").replace(",", "").strip()

            try:
                precio_num = float(precio_txt)

                try:
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

                except pyodbc.IntegrityError:
                    # Captura duplicados por índice único
                    duplicados += 1
                    logging.info(f"Duplicado ignorado: {nombre_txt}")

            except ValueError:
                logging.warning(f"Precio inválido: {precio_txt}")
                print(f"⚠️ Precio inválido: {precio_txt}")

    conn.commit()

    print(f"✅ Insertados: {contador}")
    print(f"⏭️ Duplicados ignorados: {duplicados}")

    logging.info(f"Insertados: {contador}")
    logging.info(f"Duplicados ignorados: {duplicados}")

except WebDriverException as e:
    print("❌ Error al iniciar el navegador")
    logging.error(f"Error Selenium: {e}")

except Exception as e:
    print("❌ Error durante el scraping")
    logging.error(f"Error scraping: {e}")

finally:
    if driver:
        driver.quit()
        print("🧹 Navegador cerrado")
    if conn:
        conn.close()
        print("🔒 Conexión a SQL Server cerrada")

    logging.info("===== FIN DEL SCRAPING =====")
