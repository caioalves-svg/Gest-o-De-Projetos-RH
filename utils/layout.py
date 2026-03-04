import streamlit as st
from auth.security import login

def aplicar_estilo_corporativo():
    # CSS Corrigido: Esconde o desnecessário, mantém o essencial
    st.markdown("""
        <style>
            /* 1. Esconde o menu de arquivos nativo */
            [data-testid="stSidebarNav"] {display: none;}
            
            /* 2. Esconde o botão Deploy e os 3 pontos, mas MANTÉM a seta do menu */
            [data-testid="stToolbar"] {visibility: hidden !important;}
            footer {visibility: hidden !important;}
            
            /* 3. Garante que o Header não bloqueie a visão nem quebre os ícones */
            header {
                background-color: transparent !important;
                color: transparent !important;
            }
            [data-testid="collapsedControl"] {
                color: #0F172A !important; /* Cor da setinha do menu */
            }

            /* 4. Estilo de Cartões SaaS */
            .stApp { background-color: #F8FAFC; }
            [data-testid="metric-container"] {
                background: white; border: 1px solid #E2E8F0; padding: 20px;
                border-radius: 12px; border-top: 5px solid #2563EB;
                box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            }
            
            /* 5. Botões e Inputs Arredondados */
            .stButton>button { border-radius: 8px !important; font-weight: 600 !important; width: 100%; }
            .stTextInput>div>div>input { border-radius: 8px !important; }
        </style>
    """, unsafe_allow_html=True)

    # Lógica do Menu Lateral Permanente
    if st.session_state.get('logged_in'):
        with st.sidebar:
            st.markdown(f"### 👋 Olá, {st.session_state.get('name', 'Usuário')}")
            st.caption(f"Perfil: **{st.session_state.get('role', '').upper()}**")
            st.divider()
            
            st.page_link("pages/2_📋_Projetos.py", label="Workspace de Projetos", icon="🏢")
            st.page_link("pages/3_➕_Novo_Projeto.py", label="Iniciar Novo Projeto", icon="🚀")
            
            if st.session_state.get('role') == 'admin':
                st.markdown("<br>**👑 ESTRATÉGICO**", unsafe_allow_html=True)
                st.page_link("pages/1_📊_Dashboard.py", label="Dashboard Executivo", icon="📊")
                st.page_link("pages/4_⚙️_Configuracoes.py", label="Usuários e Acessos", icon="⚙️")
            
            st.divider()
            if st.sidebar.button("🚪 Sair"):
                st.session_state.clear()
                st.rerun()
    else:
        # Formulário de login na lateral para evitar que o usuário fique "preso"
        with st.sidebar:
            st.warning("🔐 Acesso Restrito")
            with st.form("login_side"):
                u = st.text_input("Usuário")
                p = st.text_input("Senha", type="password")
                if st.form_submit_button("Entrar"):
                    if login(u, p): st.rerun()
                    else: st.error("Erro de Login")
