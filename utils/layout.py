import streamlit as st

def aplicar_estilo_corporativo():
    st.markdown("""
        <style>
            /* 1. OCULTA APENAS O MENU DIREITO (Deploy/Três Pontinhos) E O RODAPÉ */
            [data-testid="stToolbar"] {visibility: hidden !important;}
            footer {visibility: hidden !important;}
            
            /* 2. DEIXA A BARRA SUPERIOR TRANSPARENTE (Assim a setinha funciona perfeitamente) */
            header {
                background-color: transparent !important;
            }

            /* Fundo geral mais suave para destacar os cartões brancos */
            .stApp {
                background-color: #F8FAFC;
            }

            /* Estilo Premium para os Campos de Texto e Selects */
            .stTextInput>div>div>input, .stSelectbox>div>div>select, .stTextArea>div>div>textarea {
                border-radius: 8px !important;
                border: 1px solid #E2E8F0 !important;
                padding: 10px 15px !important;
                box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.02) !important;
                transition: all 0.2s ease !important;
            }
            .stTextInput>div>div>input:focus, .stSelectbox>div>div>select:focus {
                border-color: #3B82F6 !important;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
            }

            /* Estilo dos Botões - Primário e Secundário */
            .stButton>button {
                border-radius: 8px !important;
                font-weight: 600 !important;
                transition: all 0.2s ease !important;
                border: none !important;
                padding: 0.5rem 1rem !important;
            }
            
            /* Botão Primário (Form Submit) */
            [data-testid="stFormSubmitButton"]>button {
                background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
                color: white !important;
                box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2) !important;
            }
            [data-testid="stFormSubmitButton"]>button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 8px -1px rgba(37, 99, 235, 0.3) !important;
            }

            /* Cards de Métricas (Dashboard) */
            [data-testid="metric-container"] {
                background-color: #FFFFFF !important;
                border: 1px solid #E2E8F0 !important;
                padding: 20px !important;
                border-radius: 12px !important;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
                border-top: 4px solid #3B82F6 !important;
            }
            
            /* Títulos e Tipografia */
            h1, h2, h3 {
                color: #0F172A !important;
                font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
                font-weight: 700 !important;
            }
            p, span, label {
                color: #334155 !important;
                font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
            }
            
            /* Tela de Login Centralizada */
            .login-header h2 {
                color: #1E293B !important;
                margin-bottom: 5px;
            }
            .login-header p {
                color: #64748B !important;
                font-size: 0.95em;
            }
        </style>
    """, unsafe_allow_html=True)
