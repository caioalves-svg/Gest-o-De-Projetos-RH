import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.setup import DB_PATH

def render():
    st.title("➕ Iniciar Novo Projeto")
    st.markdown("<p style='color: #64748B;'>Registe uma nova iniciativa estratégica no portfólio.</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    if st.session_state.get('role') != 'admin':
        st.error("🔒 Acesso restrito a administradores.")
        return

    # Garante que a tabela de participantes existe (Autocura)
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS project_participants (
                    project_id INTEGER, 
                    user_id INTEGER, 
                    PRIMARY KEY (project_id, user_id))''')
    conn.commit()
    
    users_df = pd.read_sql_query("SELECT id, name FROM users", conn)
    conn.close()
    
    if users_df.empty:
        st.error("Erro crítico: Nenhum utilizador encontrado na base de dados.")
        return
        
    users_dict = dict(zip(users_df['id'], users_df['name']))

    col_tipo, col_vazia = st.columns([1, 2])
    tipo = col_tipo.selectbox("Tipo de Iniciativa", ["Melhoria", "Implantação"])

    with st.form("form_novo_proj", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nome = col1.text_input("Nome do Projeto*")
        manager = col2.selectbox("👤 Gestor Responsável", list(users_dict.keys()), format_func=lambda x: users_dict[x])
        
        col3, col4 = st.columns(2)
        due_date = col3.date_input("📅 Prazo Desejado", format="DD/MM/YYYY")
        # NOVO CAMPO: Múltipla escolha para a Equipa!
        equipa = col4.multiselect("👥 Membros da Equipa (Participantes)", list(users_dict.keys()), format_func=lambda x: users_dict[x])

        st.divider()
        st.markdown(f"### Escopo Específico: {tipo}")
        
        if tipo == "Melhoria":
            as_is = st.text_area("AS-IS (Situação Atual)*", help="Descreva como o processo funciona atualmente.")
            to_be = st.text_area("TO-BE (Situação Futura)*", help="Descreva como o processo deverá funcionar.")
            justificativa = ""
            beneficios = ""
        else: 
            justificativa = st.text_area("Justificativa da Implantação*", help="Explique por que é necessário.")
            beneficios = st.text_area("Benefícios Esperados*", help="Descreva os principais benefícios.")
            as_is = ""
            to_be = ""

        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.form_submit_button("🚀 Lançar Projeto no Portfólio"):
            valido = False
            if not nome:
                st.error("⚠️ O Nome do Projeto é obrigatório.")
            elif tipo == "Melhoria" and (not as_is or not to_be):
                st.error("⚠️ Para projetos de Melhoria, os campos 'AS-IS' e 'TO-BE' são obrigatórios.")
            elif tipo == "Implantação" and (not justificativa or not beneficios):
                st.error("⚠️ Para projetos de Implantação, a 'Justificativa' e os 'Benefícios Esperados' são obrigatórios.")
            else:
                valido = True

            if valido:
                try:
                    conn = sqlite3.connect(DB_PATH)
                    cur = conn.cursor()
                    
                    cur.execute("SELECT MAX(id) FROM projects")
                    max_id = cur.fetchone()[0]
                    next_id = (max_id or 0) + 1
                    code = f"HR-{next_id:03d}"
                    
                    data_prazo_str = due_date.strftime('%Y-%m-%d')
                    data_hoje_str = datetime.now().strftime('%Y-%m-%d')
                    
                    cur.execute("""INSERT INTO projects (code, name, requester, sponsor, manager_id, type, due_date, status, start_date) 
                                   VALUES (?,?,?,?,?,?,?,?,?)""", 
                                (code, nome, "", "", manager, tipo, data_prazo_str, 'Não Iniciado', data_hoje_str))
                    proj_id = cur.lastrowid
                    
                    # GRAVAR A EQUIPA NA NOVA TABELA
                    for uid in equipa:
                        cur.execute("INSERT INTO project_participants (project_id, user_id) VALUES (?,?)", (proj_id, uid))
                    
                    if tipo == "Melhoria":
                        cur.execute("INSERT INTO project_melhoria (project_id, as_is, to_be) VALUES (?,?,?)", (proj_id, as_is, to_be))
                    else:
                        cur.execute("INSERT INTO project_implantacao (project_id, justification, risk) VALUES (?,?,?)", (proj_id, justificativa, beneficios))
                    
                    conn.commit()
                    data_pt = due_date.strftime('%d/%m/%Y')
                    st.success(f"✅ Projeto **{code}** criado com sucesso! Prazo estipulado para: **{data_pt}**.")
                except Exception as e:
                    st.error(f"❌ Erro ao guardar na base de dados: {e}")
                finally:
                    conn.close()
