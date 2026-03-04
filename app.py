import streamlit as st

# REGRA DE OURO DO STREAMLIT: DEVE SER A LINHA 1
st.set_page_config(page_title="Gestão de Projetos RH", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

import sqlite3
from database.setup import init_db
from auth.security import login
from utils.layout import aplicar_css_seguro, renderizar_menu_lateral

# Inicializa o Banco de Dados
init_db()

# Inicializa as Variáveis de Estado
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'tela_atual' not in st.session_state:
    st.session_state['tela_atual'] = 'home'

# Aplica o visual independentemente da tela
aplicar_css_seguro()

# ==========================================
# MÓDULO DE LOGIN
# ==========================================
if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>⚡ Sistema de Projetos RH</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748B;'>Acesso restrito. Insira suas credenciais.</p>", unsafe_allow_html=True)
        
        with st.form("form_login_principal"):
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            
            if st.form_submit_button("Entrar no Sistema", use_container_width=True):
                if login(username, password):
                    st.rerun() # Recarrega a página para entrar no sistema
                else:
                    st.error("❌ Usuário ou senha incorretos.")

# ==========================================
# MÓDULO DO SISTEMA LOGADO (SPA)
# ==========================================
else:
    # 1. Desenha o Menu Lateral Seguro
    renderizar_menu_lateral()

    # 2. Roteador de Telas Instantâneo
    tela = st.session_state['tela_atual']

    if tela == 'home':
        st.title("🏠 Bem-vindo ao seu Workspace")
        st.markdown("---")
        st.success("✅ O sistema está online e atualizado. Utilize o menu à esquerda para navegar pelas ferramentas de forma instantânea.")

    elif tela == 'projetos':
        st.title("🏢 Workspace de Projetos")
        st.info("Aqui entrará o seu Kanban. (Código estruturado sem atrasos)")
        # Todo o código da página de Projetos virá para cá depois

    elif tela == 'novo_projeto':
        st.title("🚀 Iniciar Novo Projeto")
        if st.session_state.get('role') != 'admin':
            st.error("🔒 Acesso negado.")
        else:
            with st.form("form_novo"):
                n = st.text_input("Nome do Projeto")
                t = st.selectbox("Tipo", ["Melhoria", "Implantação"])
                if st.form_submit_button("Criar Iniciativa"):
                    st.success("A lógica de inserção vem aqui.")

    elif tela == 'dashboard':
        st.title("📊 Dashboard Executivo")
        st.metric("Exemplo de Métrica", "100%")

    elif tela == 'configuracoes':
        st.title("⚙️ Configurações e Acessos")
        st.write("Gestão de usuários.")
