"""
Scheduler - Script para programar tareas automáticas
"""
import sys
sys.path.append('.')

import schedule
import time
from datetime import datetime
from scrapers.wong import WongScraper
from scrapers.metro import MetroScraper
from scrapers.plaza_vea import PlazaVeaScraper
from services.alerts import verificar_y_notificar_alertas
from services.reports import generar_reporte_excel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_all_scrapers():
    """Ejecutar todos los scrapers"""
    logger.info("🚀 Ejecutando scrapers programados...")
    
    scrapers = [
        WongScraper(),
        MetroScraper(),
        PlazaVeaScraper()
    ]
    
    for scraper in scrapers:
        try:
            scraper.run()
        except Exception as e:
            logger.error(f"Error en scraper {scraper.tienda_nombre}: {e}")


def check_alerts():
    """Verificar y enviar alertas"""
    logger.info("🔔 Verificando alertas programadas...")
    verificar_y_notificar_alertas()


def generate_weekly_report():
    """Generar reporte semanal"""
    logger.info("📊 Generando reporte semanal...")
    fecha = datetime.now().strftime("%Y-%m-%d")
    generar_reporte_excel(f"reporte_semanal_{fecha}.xlsx")


# Programar tareas
schedule.every().day.at("06:00").do(run_all_scrapers)  # Scraping diario a las 6 AM
schedule.every(2).hours.do(check_alerts)  # Verificar alertas cada 2 horas
schedule.every().monday.at("08:00").do(generate_weekly_report)  # Reporte semanal los lunes


if __name__ == "__main__":
    logger.info("⏰ Scheduler iniciado")
    logger.info("📅 Tareas programadas:")
    logger.info("  - Scraping diario: 6:00 AM")
    logger.info("  - Verificación de alertas: cada 2 horas")
    logger.info("  - Reporte semanal: Lunes 8:00 AM")
    
    while True:
        schedule.run_pending()
        time.sleep(60)
