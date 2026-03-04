import streamlit as st

# REGRA DE OURO: Deve ser a primeira linha do arquivo
st.set_page_config(page_title="Sistema RH", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

import sqlite3
import pandas as pd
from datetime import datetime
from database.setup import init_db, DB_PATH
from auth.security import login
from utils.layout import aplicar_estilo_corporativo
from services.kpi_service import obter_metricas_gerais_sla, calcular_sla_projeto

# Inicialização
init_db()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'pagina_ativa' not in st.session_state:
    st.session_state['pagina_ativa'] = "home"

# --- FLUXO DE ACESSO ---
if not st.session_state['logged_in']:
    col_l, col_c, col_r = st.columns([1, 1.2, 1])
    with col_c:
        st.markdown("<br><br><h2>⚡ Gestão de Projetos RH</h2>", unsafe_allow_html=True)
        with st.form("login_direct"):
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar no Workspace", use_container_width=True):
                if login(u, p):
                    st.session_state['pagina_ativa'] = "home"
                    st.rerun()
                else:
                    st.error("Credenciais inválidas")
else:
    # SISTEMA LOGADO
    aplicar_estilo_corporativo()
    pagina = st.session_state['pagina_ativa']

    # 1. PÁGINA: HOME
    if pagina == "home":
        st.title("🏠 Bem-vindo ao Painel de Controle")
        st.write("Selecione uma opção no menu lateral para começar a trabalhar.")
        st.info("Dica: A navegação agora é instantânea e não recarrega a página.")

    # 2. PÁGINA: DASHBOARD (ADMIN APENAS)
    elif pagina == "dashboard":
        st.title("📊 Dashboard Executivo")
        slas = obter_metricas_gerais_sla()
        c1, c2, c3 = st.columns(3)
        c1.metric("Lead Time Médio", f"{slas['avg_lead_time']} dias")
        c2.metric("SLA de Resposta", f"{slas['avg_first_response']}h")
        st.divider()
        st.write("Estatísticas detalhadas em carregamento...")

    # 3. PÁGINA: WORKSPACE DE PROJETOS
    elif pagina == "projetos":
        st.title("🏢 Workspace de Projetos")
        # Aqui você insere o código completo que estava no pages/2_Projetos.py
        # Sem o set_page_config e sem o aplicar_estilo_corporativo (já estão no topo)
        st.write("Listagem de projetos ativos...")

    # 4. PÁGINA: NOVO PROJETO
    elif pagina == "novo":
        st.title("🚀 Iniciar Novo Projeto")
        with st.form("new_proj"):
            n = st.text_input("Nome do Projeto")
            t = st.selectbox("Tipo", ["Melhoria", "Implantação"])
            if st.form_submit_button("Lançar Projeto"):
                st.success("Projeto criado!")

    # 5. PÁGINA: CONFIGURAÇÕES
    elif pagina == "config":
        st.title("⚙️ Configurações e Acessos")
        st.write("Gerenciamento de usuários...")
