import streamlit as st

def aplicar_css_seguro():
    st.markdown("""
        <style>
            /* =========================================
               1. SEGURANÇA BASE (NUNCA MEXER AQUI)
               ========================================= */
            [data-testid="stSidebarNav"], footer, [data-testid="stToolbar"] { display: none !important; }
            header[data-testid="stHeader"] { background-color: transparent !important; }
            button[kind="header"] {
                color: #2563EB !important; background-color: #EFF6FF !important;
                border-radius: 8px !important; margin: 10px !important;
            }
            button[kind="header"] svg { fill: #2563EB !important; }
            .stApp { background-color: #F8FAFC; }
            section[data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0 !important; min-width: 280px !important; }

            /* =========================================
               2. ANIMAÇÕES GLOBAIS (O EFEITO "UAU")
               ========================================= */
            /* Fade-in e deslize para cima quando a tela carrega */
            @keyframes fadeSlideUp {
                0% { opacity: 0; transform: translateY(15px); }
                100% { opacity: 1; transform: translateY(0); }
            }
            
            /* Aplica a animação ao bloco principal onde o conteúdo é renderizado */
            .block-container {
                animation: fadeSlideUp 0.5s cubic-bezier(0.16, 1, 0.3, 1);
            }

            /* =========================================
               3. INTERAÇÕES DE BOTÕES E CARTÕES (HOVER)
               ========================================= */
            /* Botões do Menu Lateral */
            .stButton > button {
                border-radius: 8px !important; font-weight: 600 !important; text-align: left !important;
                width: 100% !important; background-color: transparent !important; color: #334155 !important;
                border: 1px solid transparent !important; 
                transition: all 0.3s ease !important; /* Transição suave */
            }
            .stButton > button:hover {
                background-color: #EFF6FF !important; color: #2563EB !important;
                transform: translateX(5px); /* Efeito de avançar levemente para a direita */
            }
            
            /* Botões Primários (Ação) */
            [data-testid="stFormSubmitButton"] > button {
                background-color: #2563EB !important; color: #FFFFFF !important; text-align: center !important;
                box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2) !important;
            }
            [data-testid="stFormSubmitButton"] > button:hover {
                background-color: #1D4ED8 !important;
                transform: translateY(-2px); /* Efeito de flutuação para cima */
                box-shadow: 0 6px 10px -1px rgba(37, 99, 235, 0.3) !important;
            }

            /* Cartões com Borda (Projetos e Kanban) */
            [data-testid="stVerticalBlockBorderWrapper"] {
                border-radius: 12px !important;
                background-color: #FFFFFF !important;
                transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
            }
            [data-testid="stVerticalBlockBorderWrapper"]:hover {
                transform: translateY(-4px); /* O cartão levanta */
                box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.08) !important; /* Sombra realista */
                border-color: #BFDBFE !important; /* Borda acende em azul claro */
            }

            /* Cartões de Métrica (Dashboard) */
            [data-testid="metric-container"] {
                background-color: #FFFFFF !important; border: 1px solid #E2E8F0 !important;
                border-radius: 12px !important; border-top: 4px solid #2563EB !important;
                box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
                transition: transform 0.2s ease;
            }
            [data-testid="metric-container"]:hover {
                transform: scale(1.02); /* Aumenta levemente de tamanho */
            }
        </style>
    """, unsafe_allow_html=True)

def renderizar_menu_lateral():
    with st.sidebar:
        st.markdown(f"### 👋 Olá, {st.session_state.get('name', 'Usuário').split()[0]}")
        st.caption(f"Perfil: **{st.session_state.get('role', '').upper()}**")
        st.divider()

        st.markdown("**📁 NAVEGAÇÃO**")
        if st.button("🏢 Workspace de Projetos"):
            st.session_state['tela_atual'] = 'projetos'
            st.rerun()
            
        if st.button("🚀 Iniciar Novo Projeto"):
            st.session_state['tela_atual'] = 'novo_projeto'
            st.rerun()

        if st.session_state.get('role') == 'admin':
            st.markdown("<br>**👑 GESTÃO**", unsafe_allow_html=True)
            if st.button("📊 Dashboard Executivo"):
                st.session_state['tela_atual'] = 'dashboard'
                st.rerun()
            if st.button("⚙️ Configurações"):
                st.session_state['tela_atual'] = 'configuracoes'
                st.rerun()

        st.divider()
        if st.button("🚪 Sair do Sistema"):
            st.session_state.clear()
            st.rerun()
