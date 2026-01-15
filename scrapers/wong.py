"""
Wong Scraper - Extrae productos de Wong.pe
"""
import sys
sys.path.append('.')

from scrapers.base_scraper import BaseScraper
from config.settings import WONG_BASE_URL


class WongScraper(BaseScraper):
    """Scraper específico para Wong.pe"""
    
    def __init__(self):
        super().__init__("Wong", WONG_BASE_URL)
        
    def get_product_selector(self):
        """
        Selector CSS para productos de Wong
        NOTA: Estos selectores pueden necesitar actualización
        """
        # Intentar varios selectores comunes
        return "div.product-item, div.ProductCard, article.product, div[data-test='product-card']"
        
    def extract_product_data(self, producto_element):
        """Extraer datos de un producto de Wong"""
        try:
            data = {}
            
            # Nombre - intentar varios selectores
            nombre_elem = (
                producto_element.select_one("p.product-title") or
                producto_element.select_one("h3.ProductCard__name") or
                producto_element.select_one("h2.product-name") or
                producto_element.select_one("[data-test='product-name']") or
                producto_element.select_one("a[class*='title']") or
                producto_element.select_one("span[class*='name']")
            )
            
            if nombre_elem:
                data['nombre'] = nombre_elem.text.strip()
            else:
                return None
                
            # Precio - intentar varios selectores
            precio_elem = (
                producto_element.select_one("span.product-prices__value") or
                producto_element.select_one("span.ProductCard__price") or
                producto_element.select_one("span[class*='price']") or
                producto_element.select_one("[data-test='product-price']") or
                producto_element.select_one("div.price span")
            )
            
            if precio_elem:
                precio_txt = precio_elem.text.replace("S/", "").replace("S/ ", "").replace(",", "").strip()
                try:
                    data['precio'] = float(precio_txt)
                except ValueError:
                    self.logger.warning(f"Precio inválido: {precio_txt}")
                    return None
            else:
                return None
                
            # URL del producto
            link_elem = (
                producto_element.select_one("a[href*='/p/']") or
                producto_element.select_one("a.product-link") or
                producto_element.find("a")
            )
            
            if link_elem and link_elem.get('href'):
                href = link_elem['href']
                data['url'] = href if href.startswith('http') else f"{self.base_url}{href}"
            else:
                data['url'] = ""
                
            # Imagen
            img_elem = producto_element.select_one("img")
            if img_elem:
                img_src = img_elem.get('src') or img_elem.get('data-src') or img_elem.get('data-lazy-src')
                if img_src:
                    data['url_imagen'] = img_src if img_src.startswith('http') else f"{self.base_url}{img_src}"
                    
            # Marca (si está disponible)
            marca_elem = (
                producto_element.select_one("span.brand") or
                producto_element.select_one("[data-test='product-brand']") or
                producto_element.select_one("div.marca")
            )
            if marca_elem:
                data['marca'] = marca_elem.text.strip()
                
            # Rating (si está disponible)
            rating_elem = producto_element.select_one("span[class*='rating'], div.rating")
            if rating_elem:
                try:
                    rating_txt = rating_elem.text.strip()
                    data['rating'] = float(rating_txt)
                except:
                    pass
                    
            return data
            
        except Exception as e:
            self.logger.error(f"Error extrayendo datos de producto Wong: {e}")
            return None


if __name__ == "__main__":
    scraper = WongScraper()
    scraper.run()
