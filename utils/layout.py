import streamlit as st

def aplicar_estilo_corporativo():
    # Injeção de CSS para transformar o Streamlit em um SaaS Moderno
    st.markdown("""
        <style>
            /* 1. LIMPEZA DO TOPO: Oculta botões de dev, mas mantém a funcionalidade do menu */
            [data-testid="stToolbar"] {visibility: hidden !important;}
            footer {visibility: hidden !important;}
            
            header {
                background-color: rgba(255, 255, 255, 0.5) !important;
                backdrop-filter: blur(8px); /* Efeito de vidro fosco no topo */
                border-bottom: 1px solid #E2E8F0;
                height: 3rem;
            }

            /* 2. BACKGROUND E TIPOGRAFIA */
            .stApp {
                background-color: #F8FAFC; /* Cinza azulado muito claro, padrão SaaS */
            }
            
            h1, h2, h3 {
                color: #0F172A !important;
                font-weight: 700 !important;
                letter-spacing: -0.025em !important;
            }

            /* 3. INPUTS E CAMPOS DE FORMULÁRIO */
            .stTextInput>div>div>input, .stSelectbox>div>div>select, .stTextArea>div>div>textarea {
                border-radius: 10px !important;
                border: 1px solid #E2E8F0 !important;
                background-color: white !important;
                padding: 12px !important;
                transition: all 0.2s ease !important;
            }
            
            .stTextInput>div>div>input:focus {
                border-color: #3B82F6 !important;
                box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1) !important;
            }

            /* 4. BOTÕES MODERNOS */
            .stButton>button {
                border-radius: 10px !important;
                font-weight: 600 !important;
                padding: 0.6rem 1.2rem !important;
                transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }

            /* Botão de "Entrar" e "Salvar" (Primário) */
            [data-testid="stFormSubmitButton"]>button {
                background: #2563EB !important;
                color: white !important;
                width: 100% !important;
                border: none !important;
            }
            
            [data-testid="stFormSubmitButton"]>button:hover {
                background: #1D4ED8 !important;
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2) !important;
            }

            /* 5. CARDS DE DASHBOARD E KANBAN */
            [data-testid="metric-container"], .stForm {
                background-color: #FFFFFF !important;
                border: 1px solid #E2E8F0 !important;
                padding: 24px !important;
                border-radius: 16px !important;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
            }
            
            /* Destaque azul no topo dos cards de métrica */
            [data-testid="metric-container"] {
                border-top: 5px solid #2563EB !important;
            }
        </style>
    """, unsafe_allow_html=True)
