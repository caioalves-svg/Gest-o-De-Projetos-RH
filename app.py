import streamlit as st

# CONFIGURAÇÃO INICIAL (Obrigatório ser a 1ª linha)
st.set_page_config(page_title="Sistema RH", layout="wide", initial_sidebar_state="expanded")

from database.setup import init_db
from utils.layout import aplicar_estilo_corporativo
from auth.security import login

# Inicialização
init_db()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'pagina_ativa' not in st.session_state:
    st.session_state['pagina_ativa'] = "home"

# 1. TELA DE LOGIN (Se não estiver logado)
if not st.session_state['logged_in']:
    col_l, col_c, col_r = st.columns([1, 1.2, 1])
    with col_c:
        st.markdown("<br><br>## ⚡ Gestão de Projetos RH", unsafe_allow_html=True)
        with st.form("login_form"):
            user = st.text_input("Usuário")
            pw = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar no Sistema", use_container_width=True):
                if login(user, pw):
                    st.session_state['pagina_ativa'] = "home"
                    st.rerun()
                else:
                    st.error("Credenciais inválidas.")

# 2. SISTEMA LOGADO (Navegação Instantânea)
else:
    aplicar_estilo_corporativo()
    
    # Roteador de Páginas (Sem carregar arquivos externos, apenas chamando a lógica)
    p = st.session_state['pagina_ativa']
    
    if p == "home":
        st.title("🏠 Bem-vindo")
        st.write("Selecione uma opção no menu lateral para começar.")
        
    elif p == "projetos":
        # Importamos a lógica da página e executamos a função principal dela
        # Para isso funcionar, você deve envolver o código das suas páginas em funções
        from views import v_projetos # Exemplo de organização
        v_projetos.render()
        
    elif p == "novo_projeto":
        from views import v_novo_projeto
        v_novo_projeto.render()
        
    elif p == "dashboard":
        from views import v_dashboard
        v_dashboard.render()
        
    elif p == "config":
        from views import v_config
        v_config.render()
