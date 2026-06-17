from flask import Flask, render_template, send_from_directory, jsonify, request, redirect, url_for, session
import sqlite3
import os
import threading
import requests # Asegúrate de que requests esté importado
import urllib.parse
import secrets
import hashlib
import base64
from main import ejecutar_bot
from config import Config
from dotenv import set_key
import random

# Configuramos '.' como carpeta de plantillas ya que index.html está en la raíz
app = Flask(__name__, template_folder='.')
app.secret_key = Config.FLASK_SECRET_KEY # Establecer la clave secreta para la sesión

def get_db_connection():
    conn = sqlite3.connect('bot_history.db')
    conn.row_factory = sqlite3.Row
    return conn

def proceso_bot_segundo_plano(tema, visual):
    try:
        ejecutar_bot(tema, visual)
    except Exception as e:
        print(f"Error en el bot: {e}")

@app.route('/')
def index():
    try:
        videos = []
        db_status = "DB no encontrada"

        # Verificamos si la base de datos existe antes de intentar la conexión
        if os.path.exists('bot_history.db'):
            try:
                conn = get_db_connection()
                videos = conn.execute('SELECT * FROM publicaciones ORDER BY fecha DESC').fetchall()
                conn.close()
                db_status = "En línea"
            except sqlite3.OperationalError:
                # La base de datos existe pero la tabla 'publicaciones' aún no se ha creado
                db_status = "Tablas no inicializadas"
        else:
            db_status = "Esperando primera ejecución del bot..."

        # Verificamos si hay una sesión activa real (evitando placeholders)
        token = Config.TIKTOK_ACCESS_TOKEN
        es_valido = token and len(token) > 20 and "tu_" not in token.lower()
        
        tk_status = "Conectado" if es_valido else "Desconectado"
        
        return render_template('index.html', videos=videos, db_status=db_status, tk_status=tk_status)
    except Exception as e:
        return f"<h1>Error crítico en el Dashboard</h1><p>{str(e)}</p><p>Asegúrate de que 'index.html' esté en la misma carpeta que 'dashboard.py'.</p>"

@app.route('/login/tiktok')
def login_tiktok():
    """Redirige al usuario a la página de autorización de TikTok."""
    # 1. Generar state para seguridad CSRF
    csrf_state = secrets.token_urlsafe(16)
    session['csrf_state'] = csrf_state

    # 2. Generar PKCE Code Verifier y Code Challenge
    code_verifier = secrets.token_urlsafe(64)
    session['code_verifier'] = code_verifier
    
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).decode().replace('=', '')

    url = "https://www.tiktok.com/v2/auth/authorize/"
    params = {
        "client_key": Config.TIKTOK_CLIENT_KEY,
        "scope": "video.upload video.publish user.info.basic",
        "response_type": "code",
        "redirect_uri": Config.TIKTOK_REDIRECT_URI,
        "state": csrf_state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256"
    }
    return redirect(f"{url}?{urllib.parse.urlencode(params)}")

@app.route('/logout/tiktok')
def logout_tiktok():
    """Limpia el token de la sesión y del archivo .env."""
    Config.TIKTOK_ACCESS_TOKEN = ""
    Config.TIKTOK_OPEN_ID = ""
    dotenv_path = os.path.join(os.getcwd(), '.env')
    set_key(dotenv_path, "TIKTOK_ACCESS_TOKEN", "")
    set_key(dotenv_path, "TIKTOK_OPEN_ID", "")
    return redirect(url_for('index'))

@app.route('/callback/tiktok')
def callback_tiktok():
    """Recibe el código de TikTok y lo cambia por un Access Token."""
    code = request.args.get('code')
    state = request.args.get('state')

    # Validar state
    if state != session.get('csrf_state'):
        return "Error: State invalido", 400

    # Recuperar code_verifier
    code_verifier = session.get('code_verifier')

    url = "https://open.tiktokapis.com/v2/oauth/token/"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "client_key": Config.TIKTOK_CLIENT_KEY,
        "client_secret": Config.TIKTOK_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": Config.TIKTOK_REDIRECT_URI,
        "code_verifier": code_verifier
    }
    try:
        response = requests.post(url, headers=headers, data=data).json()
        access_token = response.get('access_token')
        open_id = response.get('open_id') # TikTok API suele devolver el open_id junto con el access_token
        
        if access_token and open_id:
            # Actualizar Config para la sesión actual
            Config.TIKTOK_ACCESS_TOKEN = access_token
            Config.TIKTOK_OPEN_ID = open_id
            
            # Persistir en el archivo .env
            dotenv_path = os.path.join(os.getcwd(), '.env')
            set_key(dotenv_path, "TIKTOK_ACCESS_TOKEN", access_token)
            set_key(dotenv_path, "TIKTOK_OPEN_ID", open_id)
            print(f"Token y Open ID guardados: {access_token}, {open_id}")
        else:
            print(f"No se recibió access_token o open_id en la respuesta: {response}")
    except Exception as e:
        print(f"Error al obtener token: {e}")
    return redirect(url_for('index'))

@app.route('/run-manual', methods=['POST'])
def run_manual():
    data = request.get_json() or {}
    tema = data.get('tema')
    visual = data.get('visual')

    if not tema:
        # Temas rápidos para generación manual si el usuario no pone nada
        nichos = [
            {"tema": "El secreto mejor guardado de la productividad", "visual": "office focus"},
            {"tema": "Cómo la IA cambiará tu trabajo en 2025", "visual": "technology future"},
            {"tema": "3 trucos psicológicos para caerle bien a todos", "visual": "social psychology"}
        ]
        seleccion = random.choice(nichos)
        tema = seleccion["tema"]
        visual = seleccion["visual"]

    if not visual:
        visual = "modern technology"
    
    # Ejecutar en un hilo separado para no bloquear la web
    thread = threading.Thread(target=proceso_bot_segundo_plano, args=(tema, visual))
    thread.start()
    
    return jsonify({
        "status": "success", 
        "message": f"Generando video sobre: {tema}. Esto tardará unos 2-3 minutos."
    })

@app.route('/videos/<path:filename>')
def serve_video(filename):
    # Permite a Flask servir los videos generados en el directorio raíz
    return send_from_directory(os.getcwd(), filename)

if __name__ == '__main__':
    print("🚀 Dashboard iniciado en http://127.0.0.1:5000")
    app.run(debug=True, port=5000)