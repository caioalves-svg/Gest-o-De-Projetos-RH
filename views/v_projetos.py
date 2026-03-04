# Coloque esta função no topo do seu v_projetos.py (depois dos imports)
def obter_badge_status(status):
    cores = {
        'Concluído': ('#059669', '#D1FAE5'), # Verde
        'Em Execução': ('#2563EB', '#DBEAFE'), # Azul
        'Aguardando Aprovação': ('#D97706', '#FEF3C7'), # Amarelo/Laranja
        'Pausado / Bloqueado': ('#DC2626', '#FEE2E2'), # Vermelho
        'Não Iniciado': ('#475569', '#F1F5F9'), # Cinza
        'Em Planejamento': ('#7C3AED', '#EDE9FE') # Roxo
    }
    cor_texto, cor_fundo = cores.get(status, ('#475569', '#F1F5F9'))
    return f"<span style='background-color: {cor_fundo}; color: {cor_texto}; padding: 4px 10px; border-radius: 999px; font-size: 0.8em; font-weight: 600;'>{status}</span>"


# ... (resto do seu código) ...

        # E ONDE VOCÊ DESENHA OS CARTÕES (VISÃO 1: PORTFÓLIO), FAÇA ASSIM:
        if df_p.empty:
            st.info("Nenhum projeto associado ao seu perfil.")
        else:
            cols = st.columns(3)
            for idx, row in df_p.iterrows():
                with cols[idx % 3]:
                    with st.container(border=True):
                        st.markdown(f"<h3 style='margin-bottom: 0;'>{row['code']}</h3>", unsafe_allow_html=True)
                        st.write(f"**{row['name']}**")
                        
                        # Aqui usamos o Badge!
                        badge = obter_badge_status(row['status'])
                        st.markdown(f"{badge} &nbsp; <span style='color: #64748B; font-size: 0.85em;'>👤 {row['manager_name']}</span>", unsafe_allow_html=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True) # Respiro
                        if st.button("Abrir Kanban ➔", key=f"abrir_{row['id']}", use_container_width=True):
                            st.session_state['selected_project_id'] = row['id']
                            st.session_state['selected_project_data'] = row.to_dict()
                            st.rerun()
