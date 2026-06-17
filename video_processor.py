import requests
import whisper
import os
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, CompositeAudioClip
from moviepy.config import change_settings
from config import Config

# Configurar la ruta de ImageMagick para que los subtítulos funcionen en Windows
change_settings({"IMAGEMAGICK_BINARY": Config.IMAGEMAGICK_BINARY})

class VideoProcessor:
    def __init__(self):
        self._whisper_model = None

    @property
    def whisper_model(self):
        """Carga el modelo de Whisper solo cuando se necesita por primera vez."""
        if self._whisper_model is None:
            self._whisper_model = whisper.load_model("base")
        return self._whisper_model

    def descargar_fondo(self, query: str):
        headers = {"Authorization": Config.PEXELS_API_KEY}
        url = f"https://api.pexels.com/videos/search?query={query}&per_page=1&orientation=portrait"
        response = requests.get(url, headers=headers).json()
        
        if not response.get('videos'):
            print("❌ No se encontraron videos en Pexels para la búsqueda.")
            return None
            
        video_url = response['videos'][0]['video_files'][0]['link']
        video_data = requests.get(video_url).content
        path = "temp_background.mp4"
        with open(path, "wb") as f:
            f.write(video_data)
        return path

    def obtener_subtitulos(self, audio_path: str):
        result = self.whisper_model.transcribe(audio_path, language="es")
        return result['segments']

    def ensamblar(self, video_path, audio_path, segmentos, output_name):
        # 1. Procesar Audio: Mezclar narración con música de fondo
        audio_narracion = AudioFileClip(audio_path)
        
        if os.path.exists(Config.MUSIC_PATH):
            musica_fondo = (AudioFileClip(Config.MUSIC_PATH)
                            .volumex(Config.MUSIC_VOLUME)
                            .set_duration(audio_narracion.duration))
            audio_final = CompositeAudioClip([audio_narracion, musica_fondo])
        else:
            print("⚠️ No se encontró música de fondo, se usará solo la narración.")
            audio_final = audio_narracion

        # 2. Preparar el video de fondo (ajustar duración y tamaño)
        video = VideoFileClip(video_path).loop(duration=audio_final.duration)
        video = video.resize(height=Config.VIDEO_HEIGHT).crop(x_center=video.w/2, width=Config.VIDEO_WIDTH)

        # 3. Crear los clips de subtítulos dinámicos
        clips_subtitulos = []
        for s in segmentos:
            txt = (TextClip(s['text'].upper(), 
                            fontsize=70, 
                            color='yellow', 
                            font='Arial-Bold', 
                            method='caption', 
                            size=(Config.VIDEO_WIDTH*0.8, None))
                   .set_start(s['start'])
                   .set_end(s['end'])
                   .set_position('center'))
            clips_subtitulos.append(txt)

        # 4. Componer video final y exportar
        video_con_audio = video.set_audio(audio_final)
        final = CompositeVideoClip([video_con_audio] + clips_subtitulos)
        final.write_videofile(output_name, fps=Config.FPS, codec="libx264", audio_codec="aac")