import os
from dotenv import load_dotenv

load_dotenv() # Carga las variables desde un archivo .env

class Config:
    # API Keys (Ahora se leen del .env para mayor seguridad)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
    PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
    
    # TikTok API
    TIKTOK_CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY")
    TIKTOK_CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET")
    TIKTOK_REDIRECT_URI = os.getenv("TIKTOK_REDIRECT_URI", "http://localhost:5000/callback/tiktok")
    TIKTOK_ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN")
    TIKTOK_OPEN_ID = os.getenv("TIKTOK_OPEN_ID")

    # Configuración de Video
    VIDEO_WIDTH = 1080
    VIDEO_HEIGHT = 1920
    FPS = 24
    
    # Rutas de salida
    OUTPUT_DIR = "output/"

    # Configuración de ImageMagick (Necesario para Windows)
    # Asegúrate de que esta ruta apunte a tu instalación de ImageMagick
    IMAGEMAGICK_BINARY = os.getenv("IMAGEMAGICK_BINARY", r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe")

    # Música de fondo
    MUSIC_PATH = "assets/music_background.mp3"  # Asegúrate de colocar un archivo aquí
    MUSIC_VOLUME = 0.12  # Volumen bajo para no tapar la voz

    # Clave secreta para la sesión de Flask (¡Cámbiala por una cadena aleatoria y segura!)
    FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "una_clave_secreta_muy_segura_y_aleatoria_para_flask")

    # Clave de seguridad PKCE (No cambiar, se genera dinámicamente)
    CODE_VERIFIER = os.getenv("CODE_VERIFIER", "")