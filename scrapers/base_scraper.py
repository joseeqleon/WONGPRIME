"""
Base Scraper - Clase base abstracta para todos los scrapers
"""
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential
import pyodbc
import logging
import time
import sys
from datetime import datetime

# Añadir el directorio raíz al path para imports
sys.path.append('.')
from config.settings import *


class BaseScraper(ABC):
    """Clase base para todos los scrapers"""
    
    def __init__(self, tienda_nombre, base_url):
        self.tienda_nombre = tienda_nombre
        self.base_url = base_url
        self.driver = None
        self.conn = None
        self.cursor = None
        self.tienda_id = None
        
        # Configurar logging
        self.setup_logging()
        
    def setup_logging(self):
        """Configurar logging para el scraper"""
        logging.basicConfig(
            level=getattr(logging, LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(LOG_FILE),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        
    def connect_db(self):
        """Conectar a la base de datos"""
        try:
            self.logger.info(f"🔌 Conectando a SQL Server...")
            self.conn = pyodbc.connect(DATABASE_URL)
            self.cursor = self.conn.cursor()
            self.logger.info("✅ Conexión exitosa a SQL Server")
            
            # Obtener ID de la tienda
            self.cursor.execute("SELECT id FROM tiendas WHERE nombre = ?", self.tienda_nombre)
            row = self.cursor.fetchone()
            if row:
                self.tienda_id = row[0]
            else:
                self.logger.error(f"❌ Tienda '{self.tienda_nombre}' no encontrada en la base de datos")
                raise Exception(f"Tienda '{self.tienda_nombre}' no encontrada")
                
        except Exception as e:
            self.logger.error(f"❌ Error al conectar a SQL Server: {e}")
            raise
            
    def init_browser(self):
        """Inicializar navegador Selenium"""
        try:
            self.logger.info("🌐 Iniciando navegador...")
            options = Options()
            options.add_argument("--start-maximized")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            })
            self.logger.info("✅ Navegador iniciado")
            
        except Exception as e:
            self.logger.error(f"❌ Error al iniciar navegador: {e}")
            raise
            
    @retry(stop=stop_after_attempt(MAX_RETRIES), wait=wait_exponential(min=2, max=10))
    def load_page(self, url):
        """Cargar página con reintentos automáticos"""
        self.logger.info(f"📄 Cargando: {url}")
        self.driver.get(url)
        time.sleep(SCRAPING_DELAY)
        
        # Scroll para cargar contenido dinámico
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(2)
        
    def get_soup(self):
        """Obtener BeautifulSoup del HTML actual"""
        return BeautifulSoup(self.driver.page_source, "html.parser")
        
    @abstractmethod
    def get_product_selector(self):
        """Retornar selector CSS para contenedores de productos (DEBE SER IMPLEMENTADO)"""
        pass
        
    @abstractmethod
    def extract_product_data(self, producto_element):
        """Extraer datos de un elemento de producto (DEBE SER IMPLEMENTADO)
        
        Retornar: dict con keys:
            - nombre (str)
            - precio (float)
            - url (str)
            - url_imagen (str, opcional)
            - marca (str, opcional)
            - rating (float, opcional)
            - stock (int, opcional)
        """
        pass
        
    def upsert_producto(self, data, categoria_nombre):
        """Insertar o actualizar producto usando stored procedure"""
        try:
            output_param = self.cursor.execute(
                "EXEC sp_upsert_producto ?, ?, ?, ?, ?, ?, ?",
                data.get('nombre'),
                data.get('descripcion'),
                data.get('url_imagen'),
                data.get('marca'),
                categoria_nombre,
                data.get('sku'),
                0  # Output parameter placeholder
            )
            
            # Obtener el producto_id del output
            producto_id = output_param.fetchone()[0] if output_param else None
            return producto_id
            
        except Exception as e:
            self.logger.error(f"Error al insertar/actualizar producto: {e}")
            return None
            
    def insert_precio(self, producto_id, data):
        """Insertar precio del producto"""
        try:
            self.cursor.execute("""
                INSERT INTO precios 
                (producto_id, tienda_id, precio, stock, rating, url, fecha)
                VALUES (?, ?, ?, ?, ?, ?, GETDATE())
            """,
            producto_id,
            self.tienda_id,
            data.get('precio'),
            data.get('stock'),
            data.get('rating'),
            data.get('url')
            )
            return True
            
        except pyodbc.IntegrityError:
            # Duplicado - ya existe precio para hoy
            self.logger.debug(f"Precio duplicado ignorado para producto {producto_id}")
            return False
        except Exception as e:
            self.logger.error(f"Error al insertar precio: {e}")
            return False
            
    def scrape_categoria(self, categoria_path, categoria_nombre):
        """Scrapear una categoría específica"""
        url = f"{self.base_url}/{categoria_path}"
        
        self.logger.info(f"📂 Scrapeando categoría: {categoria_nombre}")
        
        try:
            self.load_page(url)
            soup = self.get_soup()
            
            productos = soup.select(self.get_product_selector())
            self.logger.info(f"📦 Productos encontrados: {len(productos)}")
            
            nuevos = 0
            actualizados = 0
            errores = 0
            
            for producto in productos:
                try:
                    data = self.extract_product_data(producto)
                    
                    if not data or not data.get('nombre') or not data.get('precio'):
                        continue
                        
                    # Insertar/actualizar producto
                    producto_id = self.upsert_producto(data, categoria_nombre)
                    
                    if producto_id:
                        # Insertar precio
                        if self.insert_precio(producto_id, data):
                            nuevos += 1
                        else:
                            actualizados += 1
                            
                except Exception as e:
                    self.logger.error(f"Error procesando producto: {e}")
                    errores += 1
                    
            self.conn.commit()
            
            self.logger.info(f"✅ Nuevos: {nuevos} | Actualizados: {actualizados} | Errores: {errores}")
            
            return {
                'encontrados': len(productos),
                'nuevos': nuevos,
                'actualizados': actualizados,
                'errores': errores
            }
            
        except Exception as e:
            self.logger.error(f"Error scrapeando categoría {categoria_nombre}: {e}")
            return None
            
    def log_scraping(self, categoria_nombre, stats, tiempo_ejecucion):
        """Registrar log de scraping en la base de datos"""
        try:
            # Obtener categoria_id
            self.cursor.execute("SELECT id FROM categorias WHERE nombre = ?", categoria_nombre)
            row = self.cursor.fetchone()
            categoria_id = row[0] if row else None
            
            self.cursor.execute("""
                INSERT INTO scraping_logs 
                (tienda_id, categoria_id, productos_encontrados, productos_nuevos, 
                 productos_actualizados, errores, tiempo_ejecucion)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            self.tienda_id,
            categoria_id,
            stats.get('encontrados', 0),
            stats.get('nuevos', 0),
            stats.get('actualizados', 0),
            stats.get('errores', 0),
            tiempo_ejecucion
            )
            self.conn.commit()
            
        except Exception as e:
            self.logger.error(f"Error logging scraping: {e}")
            
    def run(self):
        """Ejecutar el scraper para todas las categorías configuradas"""
        inicio = time.time()
        
        self.logger.info(f"===== INICIO SCRAPING: {self.tienda_nombre} =====")
        
        try:
            self.connect_db()
            self.init_browser()
            
            for categoria_path in CATEGORIAS:
                # Extraer nombre de categoría del path
                categoria_nombre = categoria_path.split('/')[-1].replace('-', ' ').title()
                
                inicio_cat = time.time()
                stats = self.scrape_categoria(categoria_path, categoria_nombre)
                tiempo_cat = int(time.time() - inicio_cat)
                
                if stats:
                    self.log_scraping(categoria_nombre, stats, tiempo_cat)
                    
        except Exception as e:
            self.logger.error(f"❌ Error general: {e}")
            
        finally:
            if self.driver:
                self.driver.quit()
                self.logger.info("🧹 Navegador cerrado")
                
            if self.conn:
                self.conn.close()
                self.logger.info("🔒 Conexión a BD cerrada")
                
            tiempo_total = int(time.time() - inicio)
            self.logger.info(f"⏱️ Tiempo total: {tiempo_total}s")
            self.logger.info(f"===== FIN SCRAPING: {self.tienda_nombre} =====")
