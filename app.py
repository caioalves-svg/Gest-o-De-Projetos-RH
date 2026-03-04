import streamlit as st
from database.setup import init_db
from auth.security import login
from utils.layout import aplicar_estilo_corporativo

# Mudado para "expanded" para o menu iniciar sempre aberto!
st.set_page_config(page_title="Sistema de Projetos RH", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

aplicar_estilo_corporativo()
init_db()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
            <div class="login-header">
                <h2>⚡ Gestão de Projetos RH</h2>
                <p>Insira as suas credenciais para aceder ao Workspace</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=True):
            username = st.text_input("Nome de Usuário", placeholder="ex: admin")
            password = st.text_input("Senha", type="password", placeholder="••••••••")
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Entrar no Sistema", use_container_width=True)
            
            if submitted:
                if not username or not password:
                    st.warning("⚠️ Preencha todos os campos.")
                elif login(username, password):
                    st.rerun()
                else:
                    st.error("❌ Credenciais inválidas. Tente novamente.")
else:
    st.markdown('<style>[data-testid="stSidebarNav"] {display: none;}</style>', unsafe_allow_html=True)

    st.sidebar.markdown(f"### 👋 Olá, {st.session_state['name'].split()[0]}")
    st.sidebar.caption(f"🛡️ Perfil: **{st.session_state['role'].upper()}**")
    st.sidebar.divider()
    
    st.sidebar.markdown("**🌐 NAVEGAÇÃO**")
    st.sidebar.page_link("pages/2_📋_Projetos.py", label="Workspace de Projetos", icon="🏢")
    st.sidebar.page_link("pages/3_➕_Novo_Projeto.py", label="Iniciar Novo Projeto", icon="🚀")
    
    if st.session_state['role'] == 'admin':
        st.sidebar.markdown("<br>**👑 ADMINISTRAÇÃO**", unsafe_allow_html=True)
        st.sidebar.page_link("pages/1_📊_Dashboard.py", label="Dashboard Executivo", icon="📊")
        st.sidebar.page_link("pages/4_⚙️_Configuracoes.py", label="Configurações & Acessos", icon="⚙️")
    
    st.sidebar.divider()
    if st.sidebar.button("🚪 Sair do Sistema", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.title("Seja bem-vindo ao seu Workspace de Projetos.")
    st.markdown("👈 **Utilize o menu lateral para iniciar a navegação.**")
