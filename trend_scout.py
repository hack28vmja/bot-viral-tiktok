from pytrends.request import TrendReq
import random

class TrendScout:
    def __init__(self):
        self.pytrends = TrendReq(hl='es-ES', tz=360)

    def obtener_tema_tendencia(self):
        """Obtiene las tendencias actuales de búsqueda en España/Latam."""
        try:
            # Obtenemos tendencias de búsqueda en tiempo real
            trending_searches = self.pytrends.trending_searches(pn='united_states').values.tolist()
            # Aplanamos la lista y elegimos una al azar
            temas = [item[0] for item in trending_searches]
            
            if temas:
                seleccion = random.choice(temas[:10]) # Top 10 tendencias
                print(f"🔥 Tendencia detectada: {seleccion}")
                return seleccion
        except Exception as e:
            print(f"⚠️ Error al conectar con Google Trends: {e}")
        
        # Fallback por si falla la API
        nichos_fallback = ["Inteligencia Artificial", "Criptomonedas", "Productividad"]
        return random.choice(nichos_fallback)