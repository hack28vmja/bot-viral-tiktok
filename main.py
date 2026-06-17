from generator import ContentGenerator
from video_processor import VideoProcessor
from tiktok_uploader import TikTokUploader
from database import Database
from config import Config
import time
import os

def ejecutar_bot(tema, nicho_visual):
    db = Database()
    
    # Asegurar que la carpeta de salida existe
    if not os.path.exists(Config.OUTPUT_DIR):
        os.makedirs(Config.OUTPUT_DIR)

    if db.tema_existe(tema):
        print(f"⚠️ El tema '{tema}' ya ha sido procesado anteriormente. Saltando para evitar duplicados.")
        return

    gen = ContentGenerator()
    proc = VideoProcessor()
    uploader = TikTokUploader()

    print("1. Generando Guion...")
    guion = gen.generar_guion(tema)
    
    print("2. Generando Audio con ElevenLabs...")
    audio_file = gen.generar_audio(guion, "temp_audio.mp3")

    print("3. Descargando fondo de Pexels...")
    video_fondo = proc.descargar_fondo(nicho_visual)

    print("4. Transcribiendo y ensamblando...")
    subs = proc.obtener_subtitulos(audio_file)
    
    nombre_video = os.path.join(Config.OUTPUT_DIR, f"video_{int(time.time())}.mp4")
    proc.ensamblar(video_fondo, audio_file, subs, nombre_video)
    print("✅ ¡Video listo para publicar!")
    
    print("5. Publicando automáticamente...")
    tags = "#IA #Tecnologia #Productividad #Viral"
    titulo_final = f"{tema} {tags}"
    uploader.subir_video(nombre_video, titulo_final)
    
    db.registrar_publicacion(tema, nombre_video)
    
    # Limpieza de archivos temporales para ahorrar espacio
    if os.path.exists(audio_file): os.remove(audio_file)
    if os.path.exists(video_fondo): os.remove(video_fondo)
    print("🧹 Archivos temporales eliminados.")

if __name__ == "__main__":
    # Si ejecutas main.py directamente, hará un video de prueba
    ejecutar_bot("El impacto de la tecnología en 2024", "modern technology")