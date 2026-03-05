import streamlit as st
import sqlite3
import pandas as pd
import bcrypt
import os
import sys
from time import sleep

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.setup import DB_PATH

def render():
    if st.session_state.get('role') != 'admin':
        st.error("🔒 Acesso restrito a administradores.")
        return

    # ==========================================
    # CABEÇALHO COM BOTÃO DE REFRESH
    # ==========================================
    col_titulo, col_btn = st.columns([8, 2])
    col_titulo.title("⚙️ Gestão de Usuários")
    
    # O botão mágico de atualizar sem deslogar
    st.markdown("<br>", unsafe_allow_html=True)
    if col_btn.button("🔄 Atualizar Tabela", use_container_width=True):
        st.rerun()

    st.markdown("---")

    # Lê os utilizadores atuais da base de dados
    conn = sqlite3.connect(DB_PATH)
    df_users = pd.read_sql_query("SELECT id, name, username, role, can_edit_tasks FROM users", conn)
    conn.close()

    # Criação das 3 abas de gestão
    tab_lista, tab_novo, tab_editar = st.tabs([
        "📋 Usuários Cadastrados", 
        "➕ Criar Novo Usuário", 
        "✏️ Editar / Excluir"
    ])

    # ==========================================
    # ABA 1: LISTAGEM
    # ==========================================
    with tab_lista:
        df_display = df_users.copy()
        df_display['can_edit_tasks'] = df_display['can_edit_tasks'].apply(lambda x: "Sim" if x else "Não")
        df_display['role'] = df_display['role'].str.upper()
        df_display.columns = ["ID", "Nome Completo", "Login", "Perfil", "Pode Editar Tarefas?"]
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)

    # ==========================================
    # ABA 2: CRIAR NOVO USUÁRIO
    # ==========================================
    with tab_novo:
        with st.form("form_new_user", clear_on_submit=True):
            col1, col2 = st.columns(2)
            name = col1.text_input("Nome Completo*")
            user = col2.text_input("Login/Username*")
            
            col3, col4 = st.columns(2)
            passw = col3.text_input("Senha*", type="password")
            role = col4.selectbox("Perfil de Acesso", ["colaborador", "admin"])
            
            p_edit = st.checkbox("Permitir que este usuário edite tarefas (Título/Prazo)?")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("Salvar Novo Usuário"):
                if name and user and passw:
                    try:
                        hashed = bcrypt.hashpw(passw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                        can_edit = 1 if p_edit or role == 'admin' else 0 
                        
                        conn = sqlite3.connect(DB_PATH)
                        conn.execute("INSERT INTO users (username, password_hash, name, role, can_edit_tasks) VALUES (?,?,?,?,?)",
                                    (user, hashed, name, role, can_edit))
                        conn.commit(); conn.close()
                        st.success(f"✅ Usuário '{name}' criado com sucesso!")
                        sleep(1) # Pausa rápida para o utilizador ler a mensagem
                        st.rerun() # Atualiza a tabela automaticamente
                    except sqlite3.IntegrityError:
                        st.error("❌ Erro: Este Login já existe.")
                    except Exception as e:
                        st.error(f"❌ Erro: {e}")
                else:
                    st.error("⚠️ Preencha todos os campos obrigatórios (*).")

    # ==========================================
    # ABA 3: EDITAR E EXCLUIR
    # ==========================================
    with tab_editar:
        st.markdown("<p style='color: #64748B;'>Selecione um utilizador abaixo para atualizar os seus dados ou removê-lo do sistema.</p>", unsafe_allow_html=True)
        
        # Dicionário para o Selectbox ficar bonito (Nome + Login)
        user_options = {row['id']: f"{row['name']} ({row['username']})" for _, row in df_users.iterrows()}
        selected_user_id = st.selectbox("Selecione o Usuário:", options=list(user_options.keys()), format_func=lambda x: user_options[x])

        if selected_user_id:
            # Obtém os dados do utilizador selecionado
            user_data = df_users[df_users['id'] == selected_user_id].iloc[0]

            col_edit, col_delete = st.columns([6, 4])

            # ÁREA DE EDIÇÃO
            with col_edit:
                with st.container(border=True):
                    st.markdown("#### ✏️ Atualizar Dados")
                    with st.form(f"edit_form_{selected_user_id}"):
                        new_name = st.text_input("Nome Completo", value=user_data['name'])
                        new_role = st.selectbox("Perfil de Acesso", ["colaborador", "admin"], index=0 if user_data['role'] == "colaborador" else 1)
                        new_can_edit = st.checkbox("Permitir editar tarefas?", value=bool(user_data['can_edit_tasks']))
                        
                        st.info("💡 Para manter a senha atual, deixe o campo abaixo em branco.")
                        new_pass = st.text_input("Nova Senha", type="password")

                        if st.form_submit_button("💾 Guardar Alterações", use_container_width=True):
                            conn = sqlite3.connect(DB_PATH)
                            cursor = conn.cursor()
                            can_edit_val = 1 if new_can_edit or new_role == 'admin' else 0

                            if new_pass: # Se digitou uma nova senha, atualiza a senha também
                                hashed = bcrypt.hashpw(new_pass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                                cursor.execute("UPDATE users SET name=?, role=?, can_edit_tasks=?, password_hash=? WHERE id=?",
                                               (new_name, new_role, can_edit_val, hashed, selected_user_id))
                            else: # Atualiza apenas os dados normais
                                cursor.execute("UPDATE users SET name=?, role=?, can_edit_tasks=? WHERE id=?",
                                               (new_name, new_role, can_edit_val, selected_user_id))
                            
                            conn.commit(); conn.close()
                            st.success("✅ Dados atualizados com sucesso!")
                            sleep(1)
                            st.rerun()

            # ÁREA DE EXCLUSÃO (ZONA DE PERIGO)
            with col_delete:
                with st.container(border=True):
                    st.markdown("<h4 style='color: #DC2626;'>🚨 Zona de Perigo</h4>", unsafe_allow_html=True)
                    
                    # Travas de Segurança
                    if selected_user_id == st.session_state['user_id']:
                        st.warning("⚠️ Você não pode excluir a sua própria conta enquanto estiver logado.")
                    elif user_data['username'] == 'admin':
                        st.warning("⚠️ A conta do Administrador Principal (Root) não pode ser apagada do sistema.")
                    else:
                        st.markdown(f"Tem a certeza que deseja excluir o acesso de **{user_data['name']}** permanentemente?")
                        if st.button("🗑️ Excluir Usuário", type="primary", use_container_width=True):
                            conn = sqlite3.connect(DB_PATH)
                            
                            # PROTEÇÃO DE DADOS: Se o usuário tinha tarefas, elas ficam sem dono (NULL) em vez de corromper a base de dados
                            conn.execute("UPDATE tasks SET assignee_id = NULL WHERE assignee_id = ?", (selected_user_id,))
                            
                            # Remove as mensagens de chat dele e, por fim, o usuário
                            conn.execute("DELETE FROM task_chats WHERE user_id = ?", (selected_user_id,))
                            conn.execute("DELETE FROM users WHERE id=?", (selected_user_id,))
                            
                            conn.commit(); conn.close()
                            st.success("✅ Usuário excluído!")
                            sleep(1)
                            st.rerun()
