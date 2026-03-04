import sqlite3
import os
import bcrypt

DB_PATH = "rh_projects.db"
UPLOAD_DIR = "uploads"

def init_db():
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Cria a tabela users base
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        name TEXT NOT NULL,
        role TEXT NOT NULL
    )
    ''')
    
    # 2. Tabelas Restantes
    cursor.execute('''CREATE TABLE IF NOT EXISTS projects (id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT UNIQUE, name TEXT NOT NULL, requester TEXT, sponsor TEXT, manager_id INTEGER, type TEXT NOT NULL, priority TEXT, complexity TEXT, start_date DATE, due_date DATE, real_end_date DATE, status TEXT, saved_value REAL DEFAULT 0.0, FOREIGN KEY(manager_id) REFERENCES users(id))''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS project_melhoria (project_id INTEGER PRIMARY KEY, as_is TEXT, problem TEXT, root_cause TEXT, to_be TEXT, impacted_kpi TEXT, metric_before TEXT, metric_after TEXT, FOREIGN KEY(project_id) REFERENCES projects(id))''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS project_implantacao (project_id INTEGER PRIMARY KEY, justification TEXT, risk TEXT, strategic_impact TEXT, resources TEXT, FOREIGN KEY(project_id) REFERENCES projects(id))''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER NOT NULL, title TEXT NOT NULL, description TEXT, assignee_id INTEGER, start_date DATE, due_date DATE, status TEXT DEFAULT 'To Do', FOREIGN KEY(project_id) REFERENCES projects(id), FOREIGN KEY(assignee_id) REFERENCES users(id))''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS task_chats (id INTEGER PRIMARY KEY AUTOINCREMENT, task_id INTEGER NOT NULL, user_id INTEGER NOT NULL, message TEXT, file_path TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(task_id) REFERENCES tasks(id), FOREIGN KEY(user_id) REFERENCES users(id))''')
    

    # ==========================================
    # MÁGICA DA MIGRAÇÃO (Previne erros de colunas faltando)
    # ==========================================
    
    # A) Migração da tabela USERS (Permissão de Editar)
    cursor.execute("PRAGMA table_info(users)")
    users_columns = [col[1] for col in cursor.fetchall()]
    if 'can_edit_tasks' not in users_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN can_edit_tasks BOOLEAN DEFAULT 0")
        cursor.execute("UPDATE users SET can_edit_tasks = 1 WHERE role = 'admin'")

    # B) Migração da tabela TASKS (Adicionando a Descrição) -> Resolve o seu erro de agora!
    cursor.execute("PRAGMA table_info(tasks)")
    tasks_columns = [col[1] for col in cursor.fetchall()]
    if 'description' not in tasks_columns:
        cursor.execute("ALTER TABLE tasks ADD COLUMN description TEXT")
        
    # ==========================================


    # 3. Cria usuário admin padrão se não existir
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        hashed = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT INTO users (username, password_hash, name, role, can_edit_tasks) VALUES (?, ?, ?, ?, ?)", 
                       ('admin', hashed.decode('utf-8'), 'Administrador', 'admin', 1))
        
    conn.commit()
    conn.close()
