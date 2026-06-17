from pexels_api import API
import requests

PEXELS_API_KEY = 'TU_API_KEY_PEXELS'

def descargar_video_fondo(query, duracion_minima=15):
    api = API(PEXELS_API_KEY)
    api.search_videos(query, page=1, results_per_page=5)
    videos = api.get_videos()

    for video in videos:
        # Buscamos videos verticales o con buena resolución
        if video.width < video.height: # Preferimos formato vertical
            video_url = video.file_res(1080, 1920).link # Full HD vertical
            
            response = requests.get(video_url, stream=True)
            with open("fondo_descargado.mp4", "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            return "fondo_descargado.mp4"
    return None
