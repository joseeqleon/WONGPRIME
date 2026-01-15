"""
Tests para scrapers
"""
import pytest
import sys
sys.path.append('.')

from scrapers.wong import WongScraper
from scrapers.metro import MetroScraper
from scrapers.plaza_vea import PlazaVeaScraper


def test_wong_scraper_init():
    """Test initialización de WongScraper"""
    scraper = WongScraper()
    assert scraper.tienda_nombre == "Wong"
    assert scraper.base_url == "https://www.wong.pe"


def test_metro_scraper_init():
    """Test initialización de MetroScraper"""
    scraper = MetroScraper()
    assert scraper.tienda_nombre == "Metro"
    assert scraper.base_url == "https://www.metro.pe"


def test_plaza_vea_scraper_init():
    """Test initialización de PlazaVeaScraper"""
    scraper = PlazaVeaScraper()
    assert scraper.tienda_nombre == "Plaza Vea"


def test_wong_product_selector():
    """Test selector de productos de Wong"""
    scraper = WongScraper()
    selector = scraper.get_product_selector()
    assert len(selector) > 0
    assert "product" in selector.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
