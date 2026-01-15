"""
Ejecutar todos los scrapers
"""
import sys
import time
from scrapers.wong import WongScraper
from scrapers.metro import MetroScraper
from scrapers.plaza_vea import PlazaVeaScraper


def main():
    print("=" * 60)
    print("WONGPRIME - Scraping Multi-Tienda")
    print("=" * 60)
    
    scrapers = [
        ("Wong", WongScraper()),
        ("Metro", MetroScraper()),
        ("Plaza Vea", PlazaVeaScraper())
    ]
    
    for nombre, scraper in scrapers:
        print(f"\n{'='*60}")
        print(f"Iniciando scraper: {nombre}")
        print(f"{'='*60}\n")
        
        try:
            scraper.run()
        except Exception as e:
            print(f"❌ Error en scraper {nombre}: {e}")
            
        # Pausa entre scrapers
        time.sleep(5)
        
    print(f"\n{'='*60}")
    print("✅ Scraping completo de todas las tiendas")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
