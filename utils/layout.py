import streamlit as st
from auth.security import login

def aplicar_estilo_corporativo():
    # CSS para esconder o menu nativo e travar o visual SaaS
    st.markdown("""
        <style>
            /* Esconde a navegação padrão de arquivos */
            [data-testid="stSidebarNav"] {display: none !important;}
            header {background: transparent !important;}
            footer {visibility: hidden;}
            .stApp { background-color: #F8FAFC; }
            
            /* Mantém a largura da sidebar fixa */
            section[data-testid="stSidebar"] {
                min-width: 300px !important;
                max-width: 300px !important;
            }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        if st.session_state.get('logged_in'):
            st.markdown(f"### 👋 Olá, {st.session_state.get('name', 'Usuário')}")
            st.caption(f"Perfil: {st.session_state.get('role', '').upper()}")
            st.divider()
            
            # Navegação Customizada (Aparece em TODAS as páginas)
            st.page_link("pages/2_📋_Projetos.py", label="Workspace de Projetos", icon="🏢")
            st.page_link("pages/3_➕_Novo_Projeto.py", label="Novo Projeto", icon="🚀")
            
            if st.session_state.get('role') == 'admin':
                st.markdown("<br>**ADMINISTRAÇÃO**", unsafe_allow_html=True)
                st.page_link("pages/1_📊_Dashboard.py", label="Dashboard Executivo", icon="📊")
                st.page_link("pages/4_⚙️_Configuracoes.py", label="Configurações", icon="⚙️")
            
            st.divider()
            if st.button("🚪 Sair", use_container_width=True):
                st.session_state.clear()
                st.rerun()
        else:
            st.warning("🔐 Login Necessário")
            with st.form("login_sidebar"):
                u = st.text_input("Usuário")
                p = st.text_input("Senha", type="password")
                if st.form_submit_button("Entrar"):
                    if login(u, p): st.rerun()
                    else: st.error("Incorreto")
            st.stop()
