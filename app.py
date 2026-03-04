import streamlit as st
from database.setup import init_db
from auth.security import login
from utils.layout import aplicar_estilo_corporativo

# Aplica configurações visuais e de página
aplicar_estilo_corporativo()

# Inicializa o banco ao rodar o app pela primeira vez
init_db()

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
    # Se logado, mostra a navegação principal na sidebar
    st.sidebar.title(f"Bem-vindo(a), {st.session_state['name']}")
    st.sidebar.caption(f"Perfil: {st.session_state['role'].upper()}")
    
    st.write("# Sistema Central de Projetos e Inovação - RH")
    st.write("Utilize o menu lateral para navegar entre Dashboard, Projetos, Kanban e Configurações.")
    
    if st.sidebar.button("Sair"):
        st.session_state.clear()
        st.rerun()
