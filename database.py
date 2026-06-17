import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name="bot_history.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS publicaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tema TEXT NOT NULL,
                fecha TEXT NOT NULL,
                archivo_video TEXT,
                estado TEXT
            )
        ''')
        self.conn.commit()

    def tema_existe(self, tema):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM publicaciones WHERE tema = ?", (tema.strip(),))
        return cursor.fetchone() is not None

    def registrar_publicacion(self, tema, archivo_video, estado="PUBLICADO"):
        cursor = self.conn.cursor()
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO publicaciones (tema, fecha, archivo_video, estado)
            VALUES (?, ?, ?, ?)
        ''', (tema.strip(), fecha, archivo_video, estado))
        self.conn.commit()