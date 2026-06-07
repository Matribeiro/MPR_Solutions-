from pyngrok import ngrok
import os

# Define a porta que o Streamlit usa por padrão
port = 8501

# Cria o túnel para o mundo
public_url = ngrok.connect(port).public_url
print(f" * O seu projeto está online aqui: {public_url}")
print(" * Copie este link e mande para o seu sócio!")

# Mantém o script rodando
try:
    input("Pressione Enter para encerrar o túnel...")
finally:
    ngrok.kill()