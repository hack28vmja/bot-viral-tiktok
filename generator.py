from google import genai
from elevenlabs.client import ElevenLabs
from elevenlabs import save
from config import Config

class ContentGenerator:
    def __init__(self):
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.voice_client = ElevenLabs(api_key=Config.ELEVENLABS_API_KEY)

    def generar_guion(self, tema: str) -> str:
        """
        Genera un guion optimizado para retención y monetización (>60s).
        """
        prompt = (
            f"Actúa como un guionista experto en TikTok para nichos de alto rendimiento. "
            f"Escribe un guion narrativo sobre: {tema}. "
            "REGLAS CRÍTICAS PARA LA MONETIZACIÓN: "
            "1. EXTENSIÓN: Debe tener entre 165 y 185 palabras para asegurar una duración de 65-70 segundos. "
            "2. ESTRUCTURA: "
            "   - GANCHO (0-5s): Una frase que rompa el scroll. "
            "   - DESARROLLO (5-55s): No uses listas de puntos. Cuenta una historia o explica conceptos en profundidad. "
            "   - CONCLUSIÓN (55-65s): Un dato sorprendente o una reflexión final. "
            "   - CTA (65s+): Una invitación a comentar o seguir. "
            "3. TONO: Conversacional, con pausas naturales (usa comas y puntos estratégicamente). "
            "Dame solo el texto de la narración, sin etiquetas como 'Gancho:' o 'Locutor:'."
        )
        
        response = self.client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt
        )
        guion = response.text.strip()
        
        # Validación simple de longitud para avisar al desarrollador
        palabras = len(guion.split())
        print(f"--- Guion generado: {palabras} palabras (~{round(palabras/2.5)} segundos) ---")
        
        return guion

    def generar_audio(self, texto: str, output_path: str):
        """
        Genera el audio usando ElevenLabs con el modelo multilingüe v2.
        """
        audio = self.voice_client.generate(
            text=texto,
            voice="Adam", # Puedes cambiar el Voice ID según tu preferencia
            model="eleven_multilingual_v2",
            voice_settings={
                "stability": 0.45,
                "similarity_boost": 0.8
            }
        )
        save(audio, output_path)
        return output_path