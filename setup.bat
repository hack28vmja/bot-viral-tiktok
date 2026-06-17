@echo off
echo [1/3] Creando entorno virtual (venv)...
python -m venv venv
echo [2/3] Activando entorno e instalando dependencias...
call .\venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
echo [3/3] ¡Listo! Para usar el bot, recuerda activar el entorno con: .\venv\Scripts\activate
pause