import streamlit as st

# PRIMEIRA LINHA DA PÁGINA
st.set_page_config(page_title="Projetos", layout="wide", initial_sidebar_state="expanded")

import sqlite3
import pandas as pd
from utils.layout import aplicar_estilo_corporativo
# ... outros imports ...

# Aplica o estilo e o menu lateral (faz o login automático se necessário)
aplicar_estilo_corporativo()

# DAQUI PARA BAIXO O SEU CÓDIGO OPERACIONAL
st.title("🏢 Workspace de Projetos")
# ... resto do código ...
