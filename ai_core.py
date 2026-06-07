# Salve este arquivo como: ai_core.py
import json
import os
from motor import ModuloMarcenaria
import streamlit as st
from google import genai
from google.genai import types
chave_secreta = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=chave_secreta)

def consultar_ia_gemini(mensagem_usuario):
    """
    Envia a mensagem para o Gemini (nova biblioteca google-genai)
    forçando a saída em formato JSON estruturado.
    """
    system_prompt = """
    Você é um projetista de marcenaria. Extraia as medidas e componentes do pedido do usuário.
    
    REGRAS OBRIGATÓRIAS:
    1. Medidas sempre em MILÍMETROS (ex: 2 metros = 2000, 80cm = 800).
    2. Valores padrão se não informado: largura 1000, altura 800, profundidade 600.
    3. "tipo_movel" deve ser uma destas opções: "armario", "gaveteiro", "torre_quente", "balcao_canto", "closet", "painel_tv", "mesa_centro".
    
    FORMATO JSON ESPERADO:
    {
        "tipo_movel": "armario",
        "largura": 2000,
        "altura": 800,
        "profundidade": 600,
        "gavetas": 0,
        "portas": 2,
        "prateleiras": 1
    }
    """

    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        # Simulador para testes caso a chave ainda não esteja configurada
        if api_key == "SUA_CHAVE_GEMINI_AQUI_DEPOIS" or not api_key:
            print("Aviso: Simulando Gemini (Chave API não configurada).")
            tipo = "armario"
            if "gavet" in mensagem_usuario.lower(): tipo = "gaveteiro"
            return {"tipo_movel": tipo, "largura": 1500, "altura": 900, "profundidade": 500, "gavetas": 3, "portas": 2, "prateleiras": 1}

        # NOVA ESTRUTURA DA BIBLIOTECA DO GOOGLE
        client = genai.Client(api_key=api_key)
        
        response = client.models.generate_content(
            model="gemini-3.5-flash", # Modelo atualizado e muito mais rápido
            contents=mensagem_usuario,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
            )
        )
        
        # O Gemini devolve o texto estruturado que transformamos em JSON
        dados_json = json.loads(response.text)
        return dados_json

    except Exception as e:
        print(f"Erro ao consultar Gemini: {e}")
        return None

def processar_pedido_ia(mensagem_usuario):
    """
    Função principal que o seu Dashboard vai chamar.
    """
    dados = consultar_ia_gemini(mensagem_usuario)
    
    if not dados:
        return {"erro": "Não consegui entender o seu pedido. Pode ser mais específico com as medidas?"}

    movel = ModuloMarcenaria(
        largura=dados["largura"], 
        altura=dados["altura"], 
        profundidade=dados["profundidade"]
    )
    
    tipo = dados["tipo_movel"]
    pecas = []
    
    # Executa a matemática do motor.py
    if tipo == "gaveteiro": pecas = movel.calcular_caixaria() + movel.calcular_fundo() + movel.calcular_gavetas(dados["gavetas"])
    elif tipo == "torre_quente": pecas = movel.calcular_torre_quente(dados["prateleiras"], dados["portas"])
    elif tipo == "balcao_canto": pecas = movel.calcular_balcao_canto_l(dados["portas"])
    elif tipo == "closet": pecas = movel.calcular_closet_aberto(dados["prateleiras"])
    elif tipo == "painel_tv": pecas = movel.calcular_painel_tv()
    elif tipo == "mesa_centro": pecas = movel.calcular_mesa_centro()
    else: pecas = movel.calcular_caixaria() + movel.calcular_fundo() + movel.adicionar_prateleiras(dados["prateleiras"]) + movel.calcular_portas_batentes(dados["portas"])

    return {
        "sucesso": True,
        "dados_lidos": dados,
        "pecas_geradas": pecas,
        "nome_modulo": f"{tipo.replace('_', ' ').title()} ({dados['largura']}x{dados['altura']}x{dados['profundidade']}mm)",
        "resumo_orcamento": movel.calcular_orcamento(pecas, 280, 1.50, dados.get("gavetas", 0), 25, dados.get("portas", 0) * 2, 6)
    }