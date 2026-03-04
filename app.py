import streamlit as st
from database.setup import init_db
from auth.security import login
from utils.layout import aplicar_estilo_corporativo

st.set_page_config(page_title="Sistema RH", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

# Chama a função que agora contém o CSS E o Menu
aplicar_estilo_corporativo()
init_db()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    # Tela de Login (centralizada)
    col_l, col_c, col_r = st.columns([1, 1.2, 1])
    with col_c:
        st.markdown("<br><br>## ⚡ Gestão de Projetos RH", unsafe_allow_html=True)
        with st.form("login_form"):
            user = st.text_input("Usuário")
            pw = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar"):
                if login(user, pw): st.rerun()
                else: st.error("Erro de login")
else:
    st.title("Central de Projetos")
    st.info("Utilize o menu lateral fixo para navegar.")
