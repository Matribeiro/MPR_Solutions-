# Salve este arquivo como: motor.py
import os
import sqlite3
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def inicializar_banco():
    """Garante a criação da tabela do histórico de propostas se não existir."""
    conn = sqlite3.connect("marcenaria.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS propostas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT NOT NULL,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            custo REAL,
            venda REAL,
            detalhes TEXT
        )
    """)
    conn.commit()
    conn.close()

def salvar_no_banco(cliente, carrinho, custo, venda):
    """Salva o resumo do ambiente no banco de dados local."""
    import json
    conn = sqlite3.connect("marcenaria.db")
    cursor = conn.cursor()
    # Converte os dados do carrinho para string para salvar no banco
    detalhes_simplificados = [
        {"nome": item["nome"], "custo": item["resumo"]["custo_total"]} 
        for item in carrinho
    ]
    cursor.execute(
        "INSERT INTO propostas (cliente, custo, venda, detalhes) VALUES (?, ?, ?, ?)",
        (cliente, custo, venda, json.dumps(detalhes_simplificados))
    )
    conn.commit()
    conn.close()

def gerar_pdf_proposta(cliente, carrinho, custo, venda, tipo_proposta="cliente"):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 18)
    p.drawString(50, 750, "Aetheris Munus - Proposta Comercial")
    p.setFont("Helvetica", 12)
    p.drawString(50, 730, f"Cliente: {cliente}")
    
    y = 690
    for i in carrinho:
        texto = f"- {i['nome']}"
        if tipo_proposta == "loja":
            texto += f" | Custo: R$ {i['resumo']['custo_total']:.2f}"
        p.drawString(60, y, texto)
        y -= 20
        
    p.drawString(50, y-20, f"Total Venda: R$ {venda:.2f}")
    if tipo_proposta == "loja":
        p.drawString(50, y-40, f"Total Custo: R$ {custo:.2f}")
        
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer.getvalue()

class ModuloMarcenaria:
    def __init__(self, largura, altura, profundidade, espessura=15):
        self.L = largura
        self.A = altura
        self.P = profundidade
        self.E = espessura

    def calcular_caixaria(self):
        """Estrutura básica padrão: 2 Laterais, 1 Base e 1 Tampo/Régua."""
        return [
            {"Peça": "Lateral Esquerda", "Quantidade": 1, "Dimensão X (mm)": self.A, "Dimensão Y (mm)": self.P},
            {"Peça": "Lateral Direita", "Quantidade": 1, "Dimensão X (mm)": self.A, "Dimensão Y (mm)": self.P},
            {"Peça": "Base Inferior", "Quantidade": 1, "Dimensão X (mm)": self.L - (2 * self.E), "Dimensão Y (mm)": self.P},
            {"Peça": "Tampo Superior", "Quantidade": 1, "Dimensão X (mm)": self.L - (2 * self.E), "Dimensão Y (mm)": self.P}
        ]

    def calcular_fundo(self):
        """Retorna o painel traseiro do móvel."""
        return [{"Peça": "Fundo Traseiro", "Quantidade": 1, "Dimensão X (mm)": self.A - 6, "Dimensão Y (mm)": self.L - 6}]

    def adicionar_prateleiras(self, qtd):
        if qtd <= 0: return []
        return [{"Peça": f"Prateleira Interna", "Quantidade": qtd, "Dimensão X (mm)": self.L - (2 * self.E) - 2, "Dimensão Y (mm)": self.P - 20}]

    def calcular_portas_batentes(self, qtd):
        if qtd <= 0: return []
        largura_porta = (self.L / qtd) - 3
        altura_porta = self.A - 4
        return [{"Peça": "Porta", "Quantidade": qtd, "Dimensão X (mm)": altura_porta, "Dimensão Y (mm)": largura_porta}]

    def calcular_gavetas(self, qtd):
        if qtd <= 0: return []
        pecas = []
        altura_frente = (self.A / qtd) - 4
        for i in range(qtd):
            pecas.append({"Peça": f"Frente Gaveta {i+1}", "Quantidade": 1, "Dimensão X (mm)": altura_frente, "Dimensão Y (mm)": self.L - 4})
            pecas.append({"Peça": f"Lateral Gaveta {i+1}", "Quantidade": 2, "Dimensão X (mm)": 150, "Dimensão Y (mm)": self.P - 50})
            pecas.append({"Peça": f"Contra-Frente Gav {i+1}", "Quantidade": 2, "Dimensão X (mm)": 130, "Dimensão Y (mm)": self.L - (4 * self.E) - 30})
        return pecas

    def calcular_torre_quente(self, prateleiras, portas):
        """Móvel alto com vãos para eletros."""
        pecas = self.calcular_caixaria() + self.calcular_fundo()
        pecas.append({"Peça": "Base do Forno (Reforçada)", "Quantidade": 1, "Dimensão X (mm)": self.L - (2 * self.E), "Dimensão Y (mm)": self.P})
        pecas.append({"Peça": "Base do Microondas", "Quantidade": 1, "Dimensão X (mm)": self.L - (2 * self.E), "Dimensão Y (mm)": self.P})
        pecas += self.adicionar_prateleiras(prateleiras)
        pecas += self.calcular_portas_batentes(portas)
        return pecas

    def calcular_balcao_canto_l(self, portas):
        return [
            {"Peça": "Lateral Externa Longa", "Quantidade": 1, "Dimensão X (mm)": self.A, "Dimensão Y (mm)": self.P},
            {"Peça": "Lateral Interna Curta", "Quantidade": 1, "Dimensão X (mm)": self.A, "Dimensão Y (mm)": self.P - 150},
            {"Peça": "Base em L (Corte Especial)", "Quantidade": 1, "Dimensão X (mm)": self.L - self.E, "Dimensão Y (mm)": self.P},
            {"Peça": "Régua Frontal de Encaixe", "Quantidade": 2, "Dimensão X (mm)": 80, "Dimensão Y (mm)": self.L - (2 * self.E)},
            {"Peça": "Porta de Canto C/ Dobradiça Especial", "Quantidade": portas, "Dimensão X (mm)": self.A - 4, "Dimensão Y (mm)": (self.L - 200) / max(portas, 1)}
        ]

    def calcular_closet_aberto(self, prateleiras):
        return [
            {"Peça": "Montante Lateral Esquerdo", "Quantidade": 1, "Dimensão X (mm)": self.A, "Dimensão Y (mm)": self.P},
            {"Peça": "Montante Lateral Direito", "Quantidade": 1, "Dimensão X (mm)": self.A, "Dimensão Y (mm)": self.P},
            {"Peça": "Base Chão", "Quantidade": 1, "Dimensão X (mm)": self.L - (2 * self.E), "Dimensão Y (mm)": self.P},
            {"Peça": "Tampo Chapéu Superior", "Quantidade": 1, "Dimensão X (mm)": self.L - (2 * self.E), "Dimensão Y (mm)": self.P}
        ] + self.adicionar_prateleiras(prateleiras)

    def calcular_painel_tv(self):
        return [
            {"Peça": "Painel Frontal Acabamento", "Quantidade": 1, "Dimensão X (mm)": self.A, "Dimensão Y (mm)": self.L},
            {"Peça": "Régua Cunha Fixação Parede", "Quantidade": 2, "Dimensão X (mm)": 100, "Dimensão Y (mm)": self.L - 100},
            {"Peça": "Régua Cunha Fixação Painel", "Quantidade": 2, "Dimensão X (mm)": 100, "Dimensão Y (mm)": self.L - 100}
        ]

    def calcular_mesa_centro(self):
        return [
            {"Peça": "Tampo Superior Visível", "Quantidade": 1, "Dimensão X (mm)": self.L, "Dimensão Y (mm)": self.P},
            {"Peça": "Laterais de Sustentação", "Quantidade": 2, "Dimensão X (mm)": self.A - self.E, "Dimensão Y (mm)": self.P},
            {"Peça": "Fechamentos Frontal/Traseiro", "Quantidade": 2, "Dimensão X (mm)": self.A - self.E, "Dimensão Y (mm)": self.L - (2 * self.E)}
        ]

    def calcular_orcamento(self, pecas, p_chapa, p_fita, q_corredica, p_corredica, q_dobradica, p_dobradica):
        area_total_m2 = 0.0
        perimetro_total_m = 0.0
        
        for p in pecas:
            x_m = p["Dimensão X (mm)"] / 1000.0
            y_m = p["Dimensão Y (mm)"] / 1000.0
            qtd = p["Quantidade"]
            
            area_total_m2 += (x_m * y_m) * qtd
            perimetro_total_m += ((x_m * 2) + (y_m * 2)) * qtd

        metros_fita = perimetro_total_m * 1.20
        custo_mdf = area_total_m2 * (p_chapa / 5.06)
        custo_fita = metros_fita * p_fita
        custo_ferragens = (q_corredica * p_corredica) + (q_dobradica * p_dobradica)
        
        custo_total = custo_mdf + custo_fita + custo_ferragens
        
        return {
            "area_mdf": area_total_m2,
            "metros_fita": metros_fita,
            "custo_ferragens": custo_ferragens,
            "custo_total": custo_total
        }