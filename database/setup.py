import sqlite3
import os

DB_PATH = "rh_projects.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabela de Usuários
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        name TEXT NOT NULL,
        role TEXT NOT NULL -- 'admin' ou 'colaborador'
    )
    ''')
    
    # Tabela de Projetos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE,
        name TEXT NOT NULL,
        requester TEXT,
        sponsor TEXT,
        manager_id INTEGER,
        type TEXT NOT NULL,
        priority TEXT,
        complexity TEXT,
        start_date DATE,
        due_date DATE,
        real_end_date DATE,
        status TEXT,
        saved_value REAL DEFAULT 0.0,
        FOREIGN KEY(manager_id) REFERENCES users(id)
    )
    ''')
    
    # Cria usuário admin padrão se não existir (senha: admin123)
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        import bcrypt
        hashed = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT INTO users (username, password_hash, name, role) VALUES (?, ?, ?, ?)", 
                       ('admin', hashed.decode('utf-8'), 'Administrador', 'admin'))
        
    conn.commit()
    conn.close()
