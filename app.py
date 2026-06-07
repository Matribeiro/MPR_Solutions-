import streamlit as st
import interface_ia
import dashboard
# Mais tarde, você fará: import dashboard

# 1. Configuração global da página (Obrigatório ser a primeira coisa)
st.set_page_config(page_title="Sistema MPR", page_icon="🚪", layout="centered")

# 2. Banco de dados temporário de usuários
USUARIOS = {
    "admin": {"senha": "123", "tela": "dashboard"},
    "vendedor": {"senha": "ia123", "tela": "ia"}
}

def tela_login():
    st.title("🚪 Login do Sistema MPR")
    st.write("Digite suas credenciais para acessar a plataforma.")

    # Caixas de texto para usuário e senha
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    # Ação do botão
    if st.button("Entrar"):
        # Verifica se o usuário existe e a senha bate
        if usuario in USUARIOS and USUARIOS[usuario]["senha"] == senha:
            # Salva o login na "memória" do navegador
            st.session_state["logado"] = True
            st.session_state["tipo_tela"] = USUARIOS[usuario]["tela"]
            st.rerun() # Recarrega a página instantaneamente
        else:
            st.error("Usuário ou senha incorretos.")

def main():
    # Se o usuário acabou de abrir o site, ele não está logado
    if "logado" not in st.session_state:
        st.session_state["logado"] = False

    # Verifica o crachá: se não estiver logado, mostra a tela de login
    if not st.session_state["logado"]:
        tela_login()
    else:
        # Botão de sair na barra lateral (Corrigido)
        if st.sidebar.button("🚪 Sair"):
            st.session_state.clear()
            st.rerun()

        # O Roteador: Direciona para a tela correta baseada no tipo de usuário
        if st.session_state["tipo_tela"] == "ia":
            # Chama a função que criamos no arquivo da IA
            interface_ia.mostrar_tela()
            
        elif st.session_state["tipo_tela"] == "dashboard":
            dashboard.mostrar_dashboard() # <-- Chama a tela real

# Inicializa o script
if __name__ == "__main__":
    main()