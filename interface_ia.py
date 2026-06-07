import streamlit as st
from ai_core import processar_pedido_ia

# Tudo foi colocado dentro desta função para o app.py poder chamar
def mostrar_tela():
    st.title("🤖 Assistente de Projetos IA")
    st.caption("Descreva o móvel que você precisa e eu farei o orçamento automaticamente.")

    if "mensagens" not in st.session_state:
        st.session_state.mensagens = [
            {"role": "assistant", "content": "Olá! Sou o assistente de marcenaria. Qual móvel vamos projetar hoje? (Ex: 'Preciso de um balcão de cozinha de 2 metros por 90cm de altura')"}
        ]

    for msg in st.session_state.mensagens:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Digite as medidas e o tipo do móvel..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.mensagens.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("Analisando seu pedido e calculando chapas..."):
                resultado = processar_pedido_ia(prompt)
                
                if "erro" in resultado:
                    st.error(resultado["erro"])
                    resposta_texto = resultado["erro"]
                else:
                    nome_movel = resultado["nome_modulo"]
                    orcamento = resultado["resumo_orcamento"]
                    dados = resultado["dados_lidos"]
                    
                    resposta_texto = f"**✅ Projeto Gerado:** {nome_movel}\n\n"
                    resposta_texto += f"📐 **Medidas entendidas:** Largura {dados['largura']}mm | Altura {dados['altura']}mm | Profundidade {dados['profundidade']}mm\n\n"
                    resposta_texto += f"🪵 **MDF Necessário:** {orcamento['area_mdf']:.2f} m²\n"
                    resposta_texto += f"💵 **Custo de Produção Estimado:** R$ {orcamento['custo_total']:.2f}"
                    
                    st.markdown(resposta_texto)
                    
                    with st.expander("Ver lista de peças gerada"):
                        pecas_limpas = []
                        for peca in resultado["pecas_geradas"]:
                            peca_nova = peca.copy()
                            peca_nova["Dimensão X (mm)"] = int(peca["Dimensão X (mm)"])
                            peca_nova["Dimensão Y (mm)"] = int(peca["Dimensão Y (mm)"])
                            pecas_limpas.append(peca_nova)
                        st.dataframe(pecas_limpas, use_container_width=True, hide_index=True)
            
            st.session_state.mensagens.append({"role": "assistant", "content": resposta_texto})