import streamlit as st
from database.setup import init_db
from auth.security import login
from utils.layout import aplicar_estilo_corporativo

# CONFIGURAÇÃO DE ESTADO INICIAL: Menu sempre expandido e Layout Wide
st.set_page_config(
    page_title="Sistema de Projetos RH", 
    page_icon="⚡", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Aplicar o visual SaaS
aplicar_estilo_corporativo()

# Inicializar Banco e Migrações
init_db()

# Gestão de Sessão
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# ==========================================
# LÓGICA DE LOGIN (GATEKEEPER)
# ==========================================
if not st.session_state['logged_in']:
    # CSS específico para centralizar o Login na tela
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {display: none;} /* Esconde a lateral no login */
        </style>
    """, unsafe_allow_html=True)
    
    col_l, col_c, col_r = st.columns([1, 1.2, 1])
    
    with col_c:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("## ⚡ Bem-vindo de volta")
        st.markdown("Acesse sua conta para gerenciar os projetos de RH.")
        
        with st.form("login_form"):
            username = st.text_input("Usuário", placeholder="Seu login...")
            password = st.text_input("Senha", type="password", placeholder="••••••••")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("Entrar no Sistema"):
                if login(username, password):
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")

# ==========================================
# WORKSPACE AUTORIZADO (MENU PERMANENTE)
# ==========================================
else:
    # Esconde o menu de navegação nativo (feio) para usarmos o nosso elegante
    st.markdown('<style>[data-testid="stSidebarNav"] {display: none;}</style>', unsafe_allow_html=True)

    # Sidebar Customizada e Fixa
    st.sidebar.markdown(f"### 👋 Olá, {st.session_state['name']}")
    st.sidebar.caption(f"Perfil: **{st.session_state['role'].upper()}**")
    st.sidebar.divider()
    
    st.sidebar.markdown("**📁 GESTÃO**")
    st.sidebar.page_link("pages/2_📋_Projetos.py", label="Workspace de Projetos", icon="🏢")
    st.sidebar.page_link("pages/3_➕_Novo_Projeto.py", label="Iniciar Novo Projeto", icon="🚀")
    
    # Menus Administrativos
    if st.session_state['role'] == 'admin':
        st.sidebar.markdown("<br>**👑 ESTRATÉGICO**", unsafe_allow_html=True)
        st.sidebar.page_link("pages/1_📊_Dashboard.py", label="Dashboard Executivo", icon="📊")
        st.sidebar.page_link("pages/4_⚙️_Configuracoes.py", label="Usuários e Acessos", icon="⚙️")
    
    st.sidebar.divider()
    
    if st.sidebar.button("🚪 Sair do Sistema", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    # Tela Inicial de Boas-Vindas
    st.title("Central de Projetos RH")
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        st.info("### 📋 Seus Projetos\nVisualize o andamento das suas entregas e interaja com a equipe.")
        if st.button("Ver Meus Projetos", type="primary"):
            st.switch_page("pages/2_📋_Projetos.py")
            
    with c2:
        st.success("### 🚀 Nova Iniciativa\nAbra um novo projeto de Melhoria ou Implantação agora.")
        if st.button("Criar Novo Projeto"):
            st.switch_page("pages/3_➕_Novo_Projeto.py")
