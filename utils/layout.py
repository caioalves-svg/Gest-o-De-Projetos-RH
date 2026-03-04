import streamlit as st

def aplicar_estilo_corporativo():
    # CSS injetado no topo para evitar flicker (piscada)
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] {display: none !important;}
            header {background: transparent !important;}
            footer {visibility: hidden;}
            .stApp { background-color: #F8FAFC; }
            section[data-testid="stSidebar"] { min-width: 280px !important; }
            
            /* Estilo dos botões do menu lateral */
            .menu-btn {
                width: 100%;
                text-align: left;
                padding: 10px;
                border-radius: 8px;
                margin-bottom: 5px;
                cursor: pointer;
            }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        if st.session_state.get('logged_in'):
            st.markdown(f"### 👋 Olá, {st.session_state['name']}")
            st.caption(f"Perfil: {st.session_state['role'].upper()}")
            st.divider()
            
            # Navegação Instantânea via Session State
            if st.button("🏢 Workspace de Projetos", use_container_width=True):
                st.session_state['pagina_ativa'] = "projetos"
                st.rerun()
                
            if st.button("🚀 Iniciar Novo Projeto", use_container_width=True):
                st.session_state['pagina_ativa'] = "novo_projeto"
                st.rerun()
            
            if st.session_state['role'] == 'admin':
                st.markdown("<br>**ESTRATÉGICO**", unsafe_allow_html=True)
                if st.button("📊 Dashboard Executivo", use_container_width=True):
                    st.session_state['pagina_ativa'] = "dashboard"
                    st.rerun()
                if st.button("⚙️ Configurações", use_container_width=True):
                    st.session_state['pagina_ativa'] = "config"
                    st.rerun()
            
            st.divider()
            if st.button("🚪 Sair", use_container_width=True):
                st.session_state.clear()
                st.rerun()
        else:
            st.stop() # Bloqueia o resto se não logado
