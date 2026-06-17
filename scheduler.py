import schedule
import time
import random
import logging
from main import ejecutar_bot
from trend_scout import TrendScout

# Configuración de logs para monitorear el bot mientras duermes
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def tarea_automatica():
    logging.info("🚀 Iniciando ciclo de publicación automática...")
    
    scout = TrendScout()
    tema_tendencia = scout.obtener_tema_tendencia()
    visual_keyword = f"{tema_tendencia} technology"
    
    try:
        ejecutar_bot(tema_tendencia, visual_keyword)
        logging.info(f"✅ Video publicado exitosamente: {tema_tendencia}")
    except Exception as e:
        logging.error(f"❌ Error en la ejecución: {e}")

# Programación de 3 videos al día en horarios de alto tráfico
schedule.every().day.at("09:00").do(tarea_automatica)
schedule.every().day.at("15:00").do(tarea_automatica)
schedule.every().day.at("21:00").do(tarea_automatica)

logging.info("🤖 Scheduler activo. El bot publicará 3 veces al día.")

if __name__ == "__main__":
    # Bucle infinito para mantener el script vivo
    while True:
        schedule.run_pending()
        time.sleep(60) # Verifica cada minuto