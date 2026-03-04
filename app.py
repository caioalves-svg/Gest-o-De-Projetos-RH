import streamlit as st
from database.setup import init_db
from auth.security import login
from utils.layout import aplicar_estilo_corporativo

aplicar_estilo_corporativo()
init_db()

# OCULTA O MENU PADRÃO DO STREAMLIT PARA CRIARMOS O NOSSO INTELIGENTE
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {display: none;}
    </style>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("🔐 Login - Gestão de Projetos RH")
    with st.form("login_form"):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")
        
        if submitted:
            if login(username, password):
                st.success("Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")
else:
    # MENU LATERAL INTELIGENTE
    st.sidebar.title(f"Bem-vindo(a), {st.session_state['name']}")
    st.sidebar.caption(f"Perfil: {st.session_state['role'].upper()}")
    st.sidebar.divider()
    
    st.sidebar.markdown("**Menu de Navegação**")
    
    # Itens que TODOS veem (Projetos e Novo Projeto)
    st.sidebar.page_link("pages/2_📋_Projetos.py", label="Projetos (Workspace)", icon="📋")
    st.sidebar.page_link("pages/3_➕_Novo_Projeto.py", label="Novo Projeto", icon="➕")
    
    # Itens exclusivos do ADMIN
    if st.session_state['role'] == 'admin':
        st.sidebar.page_link("pages/1_📊_Dashboard.py", label="Dashboard Executivo", icon="📊")
        st.sidebar.page_link("pages/4_⚙️_Configuracoes.py", label="Configurações", icon="⚙️")
    
    st.sidebar.divider()
    if st.sidebar.button("Sair / Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()
        
    st.write("# 🏢 Bem-vindo ao Sistema de Projetos RH")
    st.write("👈 Utilize o menu lateral para navegar pelas funcionalidades liberadas para o seu perfil.")
