from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
import pyodbc
from datetime import datetime
import time
import sys
import os
import io

# =============================
# SOLUCION ENCODING WINDOWS
# =============================
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

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
        "SERVER=LP\\SQLEXPRESS;"
        "DATABASE=ScrapingWong;"
        "Trusted_Connection=yes;"
    )
    cursor = conn.cursor()
    print("✅ Conexión exitosa a SQL Server")
except Exception as e:
    print("❌ Error al conectar a SQL Server")
    print(e)
    sys.exit()

# =============================
# SELENIUM (MULTI-NAVEGADOR)
# =============================
driver = None
try:
    print("🌐 Iniciando navegador automáticamente...")

    options = Options()
    options.add_argument("--start-maximized")

    # Selenium Manager detecta el navegador disponible
    driver = webdriver.Chrome(options=options)

    print("✅ Navegador iniciado correctamente")
    print(f"➡️ Accediendo a: {URL_WONG}")

    driver.get(URL_WONG)

    # Esperar carga completa
    time.sleep(8)

    # =============================
    # SCRAPING
    # =============================
    soup = BeautifulSoup(driver.page_source, "html.parser")
    productos = soup.select("div.product-item")

    print(f"📦 Productos encontrados: {len(productos)}")

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
                print(f"⚠️ Precio inválido: {precio_txt} | Producto: {nombre_txt}")

    conn.commit()
    print(f"✅ Éxito: {contador} productos insertados en la base de datos")

except WebDriverException as e:
    print("❌ Error al iniciar el navegador")
    print(e)

except Exception as e:
    print("❌ Error durante el scraping")
    print(e)

finally:
    if driver:
        driver.quit()
        print("🧹 Navegador cerrado")
    if conn:
        conn.close()
        print("🔒 Conexión a SQL Server cerrada")
