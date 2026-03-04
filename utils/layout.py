import streamlit as st

def aplicar_estilo_corporativo():
    st.set_page_config(
        page_title="HR Projects & Inno", 
        page_icon="📈", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS Customizado para deixar o layout mais limpo e profissional
    st.markdown("""
        <style>
            /* Esconde o menu padrão do Streamlit e o rodapé para um visual mais limpo */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            
            /* Ajusta os cards de métricas (KPIs) */
            div[data-testid="metric-container"] {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
            }
        </style>
    """, unsafe_allow_html=True)
