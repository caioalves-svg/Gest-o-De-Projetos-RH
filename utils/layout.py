import streamlit as st

def aplicar_css_seguro():
    st.markdown("""
        <style>
            /* LIMPEZA TOTAL DA INTERFACE NATIVA */
            [data-testid="stSidebarNav"], footer, [data-testid="stToolbar"] { display: none !important; }
            header[data-testid="stHeader"] { background-color: transparent !important; }
            
            /* A Setinha do Menu */
            button[kind="header"] {
                color: #FFFFFF !important; background-color: #2563EB !important;
                border-radius: 8px !important; margin: 12px !important;
                box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.3) !important;
            }
            button[kind="header"] svg { fill: #FFFFFF !important; }

            /* FUNDO E SCROLLBAR CUSTOMIZADA */
            .stApp { background-color: #F8FAFC; }
            ::-webkit-scrollbar { width: 8px; height: 8px; }
            ::-webkit-scrollbar-track { background: transparent; }
            ::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 10px; }
            ::-webkit-scrollbar-thumb:hover { background: #94A3B8; }

            /* MENU LATERAL (SIDEBAR) ESTILO MAC OS */
            section[data-testid="stSidebar"] {
                background-color: rgba(255, 255, 255, 0.95) !important;
                backdrop-filter: blur(10px) !important;
                border-right: 1px solid rgba(226, 232, 240, 0.8) !important;
                min-width: 280px !important;
            }

            /* Botões do Menu */
            .stButton > button {
                border-radius: 10px !important; font-weight: 600 !important; text-align: left !important;
                width: 100% !important; background-color: transparent !important; color: #475569 !important;
                border: 1px solid transparent !important; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
                padding: 12px 16px !important;
            }
            .stButton > button:hover {
                background-color: #EFF6FF !important; color: #2563EB !important;
                transform: translateX(6px); box-shadow: -4px 0px 0px 0px #2563EB !important;
            }

            /* Botões Primários (Ação) */
            [data-testid="stFormSubmitButton"] > button {
                background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
                color: #FFFFFF !important; text-align: center !important; border: none !important;
                box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25) !important;
            }
            [data-testid="stFormSubmitButton"] > button:hover {
                transform: translateY(-2px); box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4) !important;
            }

            /* CARTÕES FLUTUANTES E INPUTS */
            [data-testid="stVerticalBlockBorderWrapper"], .stForm {
                background-color: #FFFFFF !important; border: 1px solid #E2E8F0 !important;
                border-radius: 16px !important; padding: 10px !important;
                box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02) !important;
                transition: transform 0.3s ease, box-shadow 0.3s ease !important;
            }
            [data-testid="stVerticalBlockBorderWrapper"]:hover {
                transform: translateY(-4px); box-shadow: 0 12px 20px -8px rgba(37, 99, 235, 0.15) !important;
                border-color: #BFDBFE !important;
            }
            
            /* Inputs de Texto Arredondados */
            .stTextInput>div>div>input, .stSelectbox>div>div>select, .stTextArea>div>div>textarea {
                border-radius: 10px !important; border: 1px solid #E2E8F0 !important;
                padding: 12px 16px !important; transition: all 0.2s ease !important;
            }
            .stTextInput>div>div>input:focus, .stSelectbox>div>div>select:focus {
                border-color: #3B82F6 !important; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2) !important;
            }

            /* ANIMAÇÃO DE ENTRADA SUAVE */
            .block-container { animation: fadeSlideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1); }
            @keyframes fadeSlideUp {
                0% { opacity: 0; transform: translateY(20px); }
                100% { opacity: 1; transform: translateY(0); }
            }
        </style>
    """, unsafe_allow_html=True)

def renderizar_menu_lateral():
    with st.sidebar:
        # Perfil do Usuário
        st.markdown(f"<h3 style='color: #0F172A; margin-bottom: 0;'>👋 Olá, {st.session_state.get('name', 'Usuário').split()[0]}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #64748B; font-size: 0.85em; margin-top: -5px;'>🛡️ Perfil: <b>{st.session_state.get('role', '').upper()}</b></p>", unsafe_allow_html=True)
        st.divider()

        st.markdown("<p style='color: #94A3B8; font-size: 0.8em; font-weight: 700; letter-spacing: 1px;'>🚀 WORKSPACE</p>", unsafe_allow_html=True)
        if st.button("🏢 Portfólio de Projetos"):
            st.session_state['tela_atual'] = 'projetos'
            st.rerun()
            
        if st.button("➕ Iniciar Novo Projeto"):
            st.session_state['tela_atual'] = 'novo_projeto'
            st.rerun()

        if st.session_state.get('role') == 'admin':
            st.markdown("<br><p style='color: #94A3B8; font-size: 0.8em; font-weight: 700; letter-spacing: 1px;'>👑 ESTRATÉGICO</p>", unsafe_allow_html=True)
            if st.button("📊 Dashboard Executivo"):
                st.session_state['tela_atual'] = 'dashboard'
                st.rerun()
            if st.button("⚙️ Configurações & Acessos"):
                st.session_state['tela_atual'] = 'configuracoes'
                st.rerun()

        st.divider()
        
        # ==========================================
        # BOTÃO GLOBAL DE ATUALIZAR O SISTEMA
        # ==========================================
        if st.button("🔄 Atualizar Página"):
            st.rerun()  # Isto recarrega todos os dados da base de dados instantaneamente sem matar a sessão
            
        if st.button("🚪 Encerrar Sessão"):
            st.session_state.clear()
            st.rerun()
