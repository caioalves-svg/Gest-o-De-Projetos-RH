import sqlite3
import os
import bcrypt

DB_PATH = "rh_projects.db"
UPLOAD_DIR = "uploads" # Pasta raiz para os anexos do chat

def init_db():
    # 1. Garante que a pasta de uploads exista para o chat
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabela de Usuários
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        name TEXT NOT NULL,
        role TEXT NOT NULL
    )
    ''')
    
    # Tabela Base de Projetos
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

    # Tabela Específica - Melhoria
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS project_melhoria (
        project_id INTEGER PRIMARY KEY,
        as_is TEXT,
        problem TEXT,
        root_cause TEXT,
        to_be TEXT,
        impacted_kpi TEXT,
        metric_before TEXT,
        metric_after TEXT,
        FOREIGN KEY(project_id) REFERENCES projects(id)
    )
    ''')

    # Tabela Específica - Implantação
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS project_implantacao (
        project_id INTEGER PRIMARY KEY,
        justification TEXT,
        risk TEXT,
        strategic_impact TEXT,
        resources TEXT,
        FOREIGN KEY(project_id) REFERENCES projects(id)
    )
    ''')

    # Tabela de Tarefas (Kanban)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        assignee_id INTEGER,
        start_date DATE,
        due_date DATE,
        status TEXT DEFAULT 'To Do',
        FOREIGN KEY(project_id) REFERENCES projects(id),
        FOREIGN KEY(assignee_id) REFERENCES users(id)
    )
    ''')

    # NOVA TABELA: Chat Interno da Tarefa (Com suporte a anexos)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS task_chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        message TEXT,
        file_path TEXT, -- Caminho do arquivo/imagem anexado (opcional)
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(task_id) REFERENCES tasks(id),
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')
    
    # Cria usuário admin padrão se não existir (senha: admin123)
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        hashed = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT INTO users (username, password_hash, name, role) VALUES (?, ?, ?, ?)", 
                       ('admin', hashed.decode('utf-8'), 'Administrador', 'admin'))
        
    conn.commit()
    conn.close()
