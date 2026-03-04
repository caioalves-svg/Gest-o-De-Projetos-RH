import streamlit as st
from database.setup import init_db
from auth.security import login
from utils.layout import aplicar_estilo_corporativo

st.set_page_config(page_title="Sistema RH", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

aplicar_estilo_corporativo()
init_db()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    # TELA DE LOGIN CENTRALIZADA
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br><h2>⚡ Gestão de Projetos RH</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            user = st.text_input("Usuário")
            pw = st.text_input("Senha", type="password")
            if st.form_submit_button("Acessar Workspace", use_container_width=True):
                if login(user, pw):
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
else:
    st.title("Seja bem-vindo!")
    st.info("Utilize o menu lateral para navegar entre os projetos e dashboards.")
