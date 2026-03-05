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

    conn = sqlite3.connect(DB_PATH)
    users_df = pd.read_sql_query("SELECT id, name FROM users", conn)
    conn.close()
    users_dict = dict(zip(users_df['id'], users_df['name']))

    # 1. A MÁGICA ESTÁ AQUI: O selectbox fica FORA do formulário para a tela reagir na hora!
    col_tipo, col_vazia = st.columns([1, 2])
    tipo = col_tipo.selectbox("Tipo de Iniciativa", ["Melhoria", "Implantação"])

    # 2. AGORA SIM, ABRIMOS O FORMULÁRIO
    with st.form("form_novo_proj", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nome = col1.text_input("Nome do Projeto*")
        manager = col2.selectbox("Gestor Responsável", list(users_dict.keys()), format_func=lambda x: users_dict[x])
        
        due_date = st.date_input("Prazo Desejado")

        st.divider()
        st.markdown(f"### Escopo Específico: {tipo}")
        
        # 3. CAMPOS CONDICIONAIS COM BASE NO TIPO (Agora atualizam instantaneamente)
        if tipo == "Melhoria":
            as_is = st.text_area(
                "AS-IS (Situação Atual)*", 
                help="Descreva como o processo funciona atualmente, incluindo possíveis problemas, gargalos ou limitações."
            )
            to_be = st.text_area(
                "TO-BE (Situação Futura)*", 
                help="Descreva como o processo deverá funcionar após a implementação da melhoria."
            )
            justificativa = ""
            beneficios = ""
        else: # Implantação
            justificativa = st.text_area(
                "Justificativa da Implantação*", 
                help="Explique por que é necessário implantar o processo, sistema ou solução."
            )
            beneficios = st.text_area(
                "Benefícios Esperados*", 
                help="Descreva os principais benefícios que o projeto deverá trazer para a organização."
            )
            as_is = ""
            to_be = ""

        st.markdown("<br>", unsafe_allow_html=True)
        
        # 4. VALIDAÇÃO E SUBMISSÃO
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
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM projects")
                code = f"HR-{cur.fetchone()[0] + 1:03d}"
                
                cur.execute("""INSERT INTO projects (code, name, requester, sponsor, manager_id, type, due_date, status, start_date) 
                               VALUES (?,?,?,?,?,?,?,?,?)""", 
                            (code, nome, "", "", manager, tipo, due_date, 'Não Iniciado', datetime.now().strftime('%Y-%m-%d')))
                proj_id = cur.lastrowid
                
                if tipo == "Melhoria":
                    cur.execute("INSERT INTO project_melhoria (project_id, as_is, to_be) VALUES (?,?,?)", (proj_id, as_is, to_be))
                else:
                    cur.execute("INSERT INTO project_implantacao (project_id, justification, risk) VALUES (?,?,?)", (proj_id, justificativa, beneficios))
                
                conn.commit()
                conn.close()
                st.success(f"✅ Projeto {code} criado com sucesso! Já pode validar o fluxo no Workspace de Projetos.")
