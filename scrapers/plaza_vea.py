"""
Plaza Vea Scraper - Extrae productos de PlazaVea.com.pe
"""
import sys
sys.path.append('.')

from scrapers.base_scraper import BaseScraper
from config.settings import PLAZA_VEA_BASE_URL


class PlazaVeaScraper(BaseScraper):
    """Scraper específico para Plaza Vea"""
    
    def __init__(self):
        super().__init__("Plaza Vea", PLAZA_VEA_BASE_URL)
        
    def get_product_selector(self):
        """Selector CSS para productos de Plaza Vea"""
        return "div.product-item, div.ProductCard, article.product, div[data-test='product-card']"
        
    def extract_product_data(self, producto_element):
        """Extraer datos de un producto de Plaza Vea"""
        try:
            data = {}
            
            # Nombre
            nombre_elem = (
                producto_element.select_one("p.product-title") or
                producto_element.select_one("h3.ProductCard__name") or
                producto_element.select_one("h2.product-name")
            )
            
            if nombre_elem:
                data['nombre'] = nombre_elem.text.strip()
            else:
                return None
                
            # Precio
            precio_elem = (
                producto_element.select_one("span.product-prices__value") or
                producto_element.select_one("span.ProductCard__price") or
                producto_element.select_one("span[class*='price']")
            )
            
            if precio_elem:
                precio_txt = precio_elem.text.replace("S/", "").replace(",", "").strip()
                try:
                    data['precio'] = float(precio_txt)
                except ValueError:
                    return None
            else:
                return None
                
            # URL
            link_elem = producto_element.find("a")
            if link_elem and link_elem.get('href'):
                href = link_elem['href']
                data['url'] = href if href.startswith('http') else f"{self.base_url}{href}"
            else:
                data['url'] = ""
                
            # Imagen
            img_elem = producto_element.select_one("img")
            if img_elem:
                img_src = img_elem.get('src') or img_elem.get('data-src')
                if img_src:
                    data['url_imagen'] = img_src if img_src.startswith('http') else f"{self.base_url}{img_src}"
                    
            # Marca
            marca_elem = producto_element.select_one("span.brand")
            if marca_elem:
                data['marca'] = marca_elem.text.strip()
                
            return data
            
        except Exception as e:
            self.logger.error(f"Error extrayendo datos de producto Plaza Vea: {e}")
            return None


if __name__ == "__main__":
    scraper = PlazaVeaScraper()
    scraper.run()
