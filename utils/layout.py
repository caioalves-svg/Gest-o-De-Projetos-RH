import streamlit as st

def aplicar_estilo_corporativo():
    # CSS de alta performance para travar o layout
    st.markdown("""
        <style>
            /* Remove a navegação nativa e poluição visual */
            [data-testid="stSidebarNav"] {display: none !important;}
            [data-testid="stToolbar"] {visibility: hidden !important;}
            footer {visibility: hidden !important;}
            header {background-color: transparent !important;}

            /* Fundo SaaS e Sidebar fixa */
            .stApp { background-color: #F8FAFC; }
            section[data-testid="stSidebar"] { min-width: 300px !important; }

            /* Estilo dos botões de navegação lateral */
            .stButton > button {
                border-radius: 10px !important;
                text-align: left !important;
                padding: 10px 20px !important;
                margin-bottom: 5px !important;
            }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        if st.session_state.get('logged_in'):
            st.markdown(f"### 👋 Olá, {st.session_state.get('name', 'Usuário')}")
            st.caption(f"Perfil: **{st.session_state.get('role', '').upper()}**")
            st.divider()
            
            st.markdown("**📁 GESTÃO**")
            # Botões que trocam de página instantaneamente sem reload do navegador
            if st.button("🏢 Workspace de Projetos", use_container_width=True):
                st.session_state['pagina_ativa'] = "projetos"
                st.rerun()
            if st.button("🚀 Iniciar Novo Projeto", use_container_width=True):
                st.session_state['pagina_ativa'] = "novo"
                st.rerun()
            
            if st.session_state.get('role') == 'admin':
                st.markdown("<br>**👑 ESTRATÉGICO**", unsafe_allow_html=True)
                if st.button("📊 Dashboard Executivo", use_container_width=True):
                    st.session_state['pagina_ativa'] = "dashboard"
                    st.rerun()
                if st.button("⚙️ Configurações", use_container_width=True):
                    st.session_state['pagina_ativa'] = "config"
                    st.rerun()
            
            st.divider()
            if st.button("🚪 Sair do Sistema", use_container_width=True):
                st.session_state.clear()
                st.rerun()
