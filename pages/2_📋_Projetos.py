import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
import os
import sys

# Ajuste de path para importações
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.setup import DB_PATH

# Verificação de Autenticação
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("Por favor, faça login para acessar o sistema.")
    st.stop()

st.set_page_config(page_title="Projetos - HR Projects", page_icon="📋", layout="wide")
st.title("📋 Gestão de Projetos")

user_id = st.session_state['user_id']
user_role = st.session_state['role']

# Funções de Banco de Dados
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

def create_project(data, specific_data, is_melhoria):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Inserir Projeto Base
    cursor.execute('''
        INSERT INTO projects (code, name, requester, sponsor, manager_id, type, priority, complexity, start_date, due_date, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data['code'], data['name'], data['requester'], data['sponsor'], data['manager_id'], 
          data['type'], data['priority'], data['complexity'], data['start_date'], data['due_date'], 'Backlog'))
    
    project_id = cursor.lastrowid
    
    # Inserir Dados Específicos
    if is_melhoria:
        cursor.execute('''
            INSERT INTO project_melhoria (project_id, as_is, problem, root_cause, to_be, impacted_kpi, metric_before, metric_after)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (project_id, specific_data['as_is'], specific_data['problem'], specific_data['root_cause'], 
              specific_data['to_be'], specific_data['impacted_kpi'], specific_data['metric_before'], specific_data['metric_after']))
    else:
        cursor.execute('''
            INSERT INTO project_implantacao (project_id, justification, risk, strategic_impact, resources)
            VALUES (?, ?, ?, ?, ?)
        ''', (project_id, specific_data['justification'], specific_data['risk'], 
              specific_data['strategic_impact'], specific_data['resources']))
        
    conn.commit()
    conn.close()

def create_task(project_id, title, assignee_id, start_date, due_date):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tasks (project_id, title, assignee_id, start_date, due_date, status)
        VALUES (?, ?, ?, ?, ?, 'To Do')
    ''', (project_id, title, assignee_id, start_date, due_date))
    conn.commit()
    conn.close()

# Estrutura de Abas (Tabs)
if user_role == 'admin':
    tab_list, tab_create = st.tabs(["📂 Listagem e Detalhes", "➕ Novo Projeto"])
else:
    tab_list, = st.tabs(["📂 Meus Projetos"])

# ==========================================
# ABA 1: LISTAGEM E DETALHES (Visível para todos)
# ==========================================
with tab_list:
    st.subheader("Projetos em Andamento e Concluídos")
    
    conn = sqlite3.connect(DB_PATH)
    if user_role == 'admin':
        query = "SELECT * FROM projects"
        df_projects = pd.read_sql_query(query, conn)
    else:
        query = """
            SELECT DISTINCT p.* FROM projects p
            LEFT JOIN tasks t ON p.id = t.project_id
            WHERE p.manager_id = ? OR t.assignee_id = ?
        """
        df_projects = pd.read_sql_query(query, conn, params=(user_id, user_id))
    conn.close()

    if df_projects.empty:
        st.info("Nenhum projeto encontrado.")
    else:
        # Exibir projetos usando expanders para ver detalhes
        users_dict = get_users()
        
        for _, row in df_projects.iterrows():
            manager_name = users_dict.get(row['manager_id'], 'Desconhecido')
            status_color = "🟢" if row['status'] == 'Concluído' else "🟡" if row['status'] in ['Em Progresso', 'Backlog'] else "🔴"
            
            with st.expander(f"{status_color} [{row['code']}] {row['name']} - {row['status']}"):
                col_info1, col_info2, col_info3 = st.columns(3)
                col_info1.write(f"**Tipo:** {row['type']}")
                col_info1.write(f"**Gerente:** {manager_name}")
                col_info2.write(f"**Prioridade:** {row['priority']}")
                col_info2.write(f"**Complexidade:** {row['complexity']}")
                col_info3.write(f"**Início:** {row['start_date']}")
                col_info3.write(f"**Prazo:** {row['due_date']}")
                
                # Admin pode alterar status, data real de conclusão e valor economizado
                if user_role == 'admin':
                    st.divider()
                    st.write("🛠️ **Ações Administrativas**")
                    with st.form(key=f"admin_actions_{row['id']}"):
                        col_a1, col_a2, col_a3 = st.columns(3)
                        new_status = col_a1.selectbox("Status", ["Backlog", "Em Progresso", "Concluído", "Atrasado"], index=["Backlog", "Em Progresso", "Concluído", "Atrasado"].index(row['status']))
                        real_end = col_a2.date_input("Data Real de Conclusão", value=pd.to_datetime(row['real_end_date']) if pd.notnull(row['real_end_date']) else None)
                        saved_val = col_a3.number_input("Valor Economizado (R$)", value=float(row['saved_value']) if pd.notnull(row['saved_value']) else 0.0, step=100.0)
                        
                        if st.form_submit_button("Atualizar Projeto"):
                            conn = sqlite3.connect(DB_PATH)
                            c = conn.cursor()
                            c.execute("UPDATE projects SET status=?, real_end_date=?, saved_value=? WHERE id=?", 
                                      (new_status, real_end, saved_val, row['id']))
                            conn.commit()
                            conn.close()
                            st.success("Atualizado!")
                            st.rerun()

                    # Admin pode criar tarefas para o projeto
                    st.write("➕ **Adicionar Tarefa ao Projeto**")
                    with st.form(key=f"new_task_{row['id']}"):
                        t_title = st.text_input("Título da Tarefa")
                        col_t1, col_t2, col_t3 = st.columns(3)
                        t_assignee = col_t1.selectbox("Responsável", options=list(users_dict.keys()), format_func=lambda x: users_dict[x])
                        t_start = col_t2.date_input("Data de Início")
                        t_due = col_t3.date_input("Prazo da Tarefa")
                        
                        if st.form_submit_button("Criar Tarefa"):
                            create_task(row['id'], t_title, t_assignee, t_start, t_due)
                            st.success("Tarefa criada! Ela já aparecerá no Kanban.")
                            st.rerun()

# ==========================================
# ABA 2: NOVO PROJETO (Apenas Admin)
# ==========================================
if user_role == 'admin':
    with tab_create:
        st.subheader("Cadastrar Novo Projeto")
        
        with st.form("form_new_project"):
            # Informações Básicas
            st.markdown("##### 📌 Identificação")
            col1, col2 = st.columns([3, 1])
            p_name = col1.text_input("Nome do Projeto*")
            p_code = col2.text_input("Código", value=generate_project_code(), disabled=True)
            
            col3, col4, col5 = st.columns(3)
            p_requester = col3.text_input("Área Solicitante*")
            p_sponsor = col4.text_input("Sponsor*")
            
            users_dict = get_users()
            p_manager = col5.selectbox("Gerente do Projeto*", options=list(users_dict.keys()), format_func=lambda x: users_dict[x])
            
            col6, col7, col8 = st.columns(3)
            p_priority = col6.selectbox("Prioridade", ["Baixa", "Média", "Alta"])
            p_complexity = col7.selectbox("Complexidade", ["Baixa", "Média", "Alta"])
            p_type = col8.radio("Tipo de Projeto*", ["Melhoria", "Implantação"], horizontal=True)
            
            col9, col10 = st.columns(2)
            p_start = col9.date_input("Data de Início Prevista")
            p_due = col10.date_input("Data Prevista de Entrega")
            
            st.divider()
            
            # Campos Dinâmicos (Streamlit re-renderiza form, mas dentro do form o st.radio funciona para layout condicional se usarmos session_state, 
            # porém no Streamlit st.form bloqueia interatividade até o submit. Para contornar e mostrar campos dinâmicos, vamos mostrar todos e validar no backend, ou fechar o form principal).
            # Como st.form não permite updates dinâmicos em tempo real do st.radio, renderizamos ambos os blocos e avisamos o usuário para preencher o correspondente.
            st.markdown("##### 🔎 Detalhamento Específico")
            st.info("Preencha apenas a coluna correspondente ao Tipo de Projeto selecionado acima.")
            
            col_melhoria, col_implanta = st.columns(2)
            
            with col_melhoria:
                st.markdown("**Se for Melhoria:**")
                m_as_is = st.text_area("As-Is (Cenário Atual)")
                m_problem = st.text_input("Problema Identificado")
                m_root = st.text_input("Causa Raiz")
                m_to_be = st.text_area("To-Be (Cenário Futuro)")
                m_kpi = st.text_input("Indicador Impactado")
                m_before = st.text_input("Métrica Antes")
                m_after = st.text_input("Métrica Depois")
                
            with col_implanta:
                st.markdown("**Se for Implantação:**")
                i_just = st.text_area("Justificativa")
                i_risk = st.text_area("Risco da Não Implantação")
                i_impact = st.text_input("Impacto Estratégico")
                i_resources = st.text_area("Recursos Necessários")
                
            submit_project = st.form_submit_button("💾 Salvar Projeto", type="primary")
            
            if submit_project:
                if not p_name or not p_requester or not p_sponsor:
                    st.error("Preencha os campos obrigatórios (*).")
                else:
                    base_data = {
                        'code': p_code, 'name': p_name, 'requester': p_requester, 'sponsor': p_sponsor,
                        'manager_id': p_manager, 'type': p_type, 'priority': p_priority, 
                        'complexity': p_complexity, 'start_date': p_start, 'due_date': p_due
                    }
                    
                    if p_type == "Melhoria":
                        spec_data = {
                            'as_is': m_as_is, 'problem': m_problem, 'root_cause': m_root,
                            'to_be': m_to_be, 'impacted_kpi': m_kpi, 'metric_before': m_before, 'metric_after': m_after
                        }
                        create_project(base_data, spec_data, is_melhoria=True)
                    else:
                        spec_data = {
                            'justification': i_just, 'risk': i_risk, 'strategic_impact': i_impact, 'resources': i_resources
                        }
                        create_project(base_data, spec_data, is_melhoria=False)
                        
                    st.success(f"Projeto {p_code} criado com sucesso!")
                    st.rerun()
