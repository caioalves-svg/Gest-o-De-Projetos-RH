import streamlit as st
import sqlite3
import pandas as pd
import os
import sys

# Ajuste de paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.setup import DB_PATH
from auth.security import check_auth

# 1. Verificação de Segurança e Perfil
check_auth()

if st.session_state.get('role') != 'admin':
    st.error("🔒 Acesso Restrito. Apenas administradores podem iniciar novos projetos.")
    st.stop()

st.set_page_config(page_title="Novo Projeto", page_icon="➕", layout="wide")

st.title("➕ Iniciar Novo Projeto")
st.markdown("Preencha o formulário abaixo para registar uma nova iniciativa no Portfólio do RH.")
st.divider()

# ==========================================
# FUNÇÕES AUXILIARES
# ==========================================
def get_users():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT id, name FROM users", conn)
    conn.close()
    return dict(zip(df['id'], df['name']))

def generate_project_code():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(id) FROM projects")
    count = cursor.fetchone()[0]
    conn.close()
    return f"HR-{count + 1:03d}"

def save_project(base_data, spec_data, is_melhoria):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Inserir Projeto Base com o status inicial de mercado ("Não Iniciado")
    cursor.execute('''
        INSERT INTO projects (code, name, requester, sponsor, manager_id, type, priority, complexity, start_date, due_date, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (base_data['code'], base_data['name'], base_data['requester'], base_data['sponsor'], base_data['manager_id'], 
          base_data['type'], base_data['priority'], base_data['complexity'], base_data['start_date'], base_data['due_date'], 'Não Iniciado'))
    
    project_id = cursor.lastrowid
    
    # Inserir Dados Específicos
    if is_melhoria:
        cursor.execute('''
            INSERT INTO project_melhoria (project_id, as_is, problem, root_cause, to_be, impacted_kpi, metric_before, metric_after)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (project_id, spec_data['as_is'], spec_data['problem'], spec_data['root_cause'], 
              spec_data['to_be'], spec_data['impacted_kpi'], spec_data['metric_before'], spec_data['metric_after']))
    else:
        cursor.execute('''
            INSERT INTO project_implantacao (project_id, justification, risk, strategic_impact, resources)
            VALUES (?, ?, ?, ?, ?)
        ''', (project_id, spec_data['justification'], spec_data['risk'], 
              spec_data['strategic_impact'], spec_data['resources']))
        
    conn.commit()
    conn.close()

# ==========================================
# FORMULÁRIO DE CRIAÇÃO (UI ENTERPRISE)
# ==========================================
with st.container(border=True):
    st.markdown("### 📌 Identificação Estratégica")
    
    col1, col2 = st.columns([3, 1])
    p_name = col1.text_input("Nome da Iniciativa*")
    p_code = col2.text_input("Código Gerado", value=generate_project_code(), disabled=True)
    
    col3, col4, col5 = st.columns(3)
    p_requester = col3.text_input("Área Solicitante*")
    p_sponsor = col4.text_input("Sponsor Executivo*")
    
    users_dict = get_users()
    if not users_dict:
        st.warning("Ainda não há utilizadores cadastrados para atribuir a gerência.")
        st.stop()
        
    p_manager = col5.selectbox("Gestor do Projeto*", options=list(users_dict.keys()), format_func=lambda x: users_dict[x])
    
    col6, col7, col8 = st.columns(3)
    p_priority = col6.selectbox("Prioridade", ["Baixa", "Média", "Alta"], index=1)
    p_complexity = col7.selectbox("Complexidade", ["Baixa", "Média", "Alta"], index=1)
    p_type = col8.radio("Classificação do Projeto*", ["Melhoria", "Implantação"], horizontal=True)
    
    col9, col10 = st.columns(2)
    p_start = col9.date_input("Data de Início")
    p_due = col10.date_input("Prazo de Entrega (Due Date)")

st.markdown("<br>", unsafe_allow_html=True)

with st.container(border=True):
    st.markdown("### 🔎 Detalhamento Específico")
    st.info(f"Preencha o escopo de **{p_type}** abaixo.")
    
    # Variáveis para guardar os dados específicos
    spec_data = {}
    
    with st.form("form_escopo", clear_on_submit=True):
        if p_type == "Melhoria":
            col_m1, col_m2 = st.columns(2)
            spec_data['as_is'] = col_m1.text_area("As-Is (Cenário Atual)")
            spec_data['problem'] = col_m1.text_input("Problema Identificado")
            spec_data['root_cause'] = col_m1.text_input("Causa Raiz")
            
            spec_data['to_be'] = col_m2.text_area("To-Be (Cenário Futuro)")
            spec_data['impacted_kpi'] = col_m2.text_input("KPI Impactado")
            
            col_met1, col_met2 = st.columns(2)
            spec_data['metric_before'] = col_met1.text_input("Métrica Antes")
            spec_data['metric_after'] = col_met2.text_input("Métrica Depois")
            
        else: # Implantação
            spec_data['justification'] = st.text_area("Justificativa Estratégica")
            spec_data['risk'] = st.text_area("Risco da Não Implantação")
            
            col_i1, col_i2 = st.columns(2)
            spec_data['strategic_impact'] = col_i1.text_input("Impacto Estratégico (Curto/Longo Prazo)")
            spec_data['resources'] = col_i2.text_area("Recursos Necessários (Ferramentas, Pessoas, Orçamento)")
            
        st.markdown("<br>", unsafe_allow_html=True)
        submit_btn = st.form_submit_button("🚀 Lançar Projeto no Portfólio", type="primary", use_container_width=True)
        
        if submit_btn:
            if not p_name or not p_requester or not p_sponsor:
                st.error("Por favor, preencha todos os campos obrigatórios (*).")
            else:
                base_data = {
                    'code': p_code, 'name': p_name, 'requester': p_requester, 'sponsor': p_sponsor,
                    'manager_id': p_manager, 'type': p_type, 'priority': p_priority, 
                    'complexity': p_complexity, 'start_date': p_start, 'due_date': p_due
                }
                
                save_project(base_data, spec_data, is_melhoria=(p_type == "Melhoria"))
                st.success(f"Projeto '{p_name}' criado com sucesso! Ele já está disponível no Portfólio.")
