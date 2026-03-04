import sqlite3
import os

DB_PATH = "rh_projects.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Tabela de Usuários
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        name TEXT NOT NULL,
        role TEXT NOT NULL
    )
    ''')
    
    # 2. Tabela Base de Projetos
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

    # 3. Tabela Específica - Melhoria
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

    # 4. Tabela Específica - Implantação
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

    # 5. Tabela de Tarefas (Kanban)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        title TEXT,
        assignee_id INTEGER,
        start_date DATE,
        due_date DATE,
        status TEXT,
        FOREIGN KEY(project_id) REFERENCES projects(id),
        FOREIGN KEY(assignee_id) REFERENCES users(id)
    )
    ''')

    # 6. Tabela de Comentários (Interações/SLA)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        task_id INTEGER,
        user_id INTEGER,
        content TEXT,
        created_at DATETIME,
        FOREIGN KEY(project_id) REFERENCES projects(id),
        FOREIGN KEY(task_id) REFERENCES tasks(id),
        FOREIGN KEY(user_id) REFERENCES users(id)
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
