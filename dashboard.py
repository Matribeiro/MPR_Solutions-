import streamlit as st
import io, csv
import os
from motor import ModuloMarcenaria, inicializar_banco, salvar_no_banco, gerar_pdf_proposta

def mostrar_dashboard():
    # Inicialização do banco de dados
    inicializar_banco()
    
    # CARREGAMENTO ROBUSTO DA LOGO (Caminho absoluto)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(script_dir, "logo.jpg") # Mude para .png se a imagem for PNG

    st.sidebar.title("Navegação")
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, use_container_width=True)
    else:
        st.sidebar.warning(f"Logo não encontrada em: {logo_path}")

    st.sidebar.markdown("---")

    # ==========================================
    # 🎨 INJEÇÃO DE ESTILO CSS PREMIUM
    # ==========================================
    st.markdown("""
    <style>
        /* Cards de métricas */
        [data-testid="stMetric"] {
            background-color: #161922 !important;
            border: 1px solid #2d3345 !important;
            padding: 15px 20px !important;
            border-radius: 12px !important;
            box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.4) !important;
            transition: all 0.2s ease-in-out !important;
        }
        [data-testid="stMetric"]:hover {
            transform: translateY(-2px) !important;
            border-color: #00b4d8 !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.9rem !important;
            color: #94a3b8 !important;
            font-weight: 500 !important;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.6rem !important;
            font-weight: 700 !important;
        }

        /* Centralização de botões */
        div[data-testid="stButton"] button, div[data-testid="stDownloadButton"] button {
            display: block !important;
            width: 100% !important;
            max-width: 340px !important;
            margin: 0 auto !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: all 0.25s ease-in-out !important;
            background-color: #1c202a !important;
            color: #e0e2e8 !important;
            border: 1px solid #383f51 !important;
        }
        div[data-testid="stButton"] button:hover, div[data-testid="stDownloadButton"] button:hover {
            border-color: #00b4d8 !important;
            color: #00b4d8 !important;
            background-color: #222733 !important;
        }
        div[data-testid="stButton"] button[data-testid="stBaseButton-primary"] {
            background: linear-gradient(135deg, #00bc62, #009e4f) !important;
            color: white !important;
            border: none !important;
            box-shadow: 0px 3px 10px rgba(0, 188, 98, 0.2) !important;
        }
        div[data-testid="stButton"] button[data-testid="stBaseButton-primary"]:hover {
            box-shadow: 0px 5px 15px rgba(0, 188, 98, 0.4) !important;
            filter: brightness(1.1) !important;
            color: white !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("📐 MPR Solutions")
    st.caption("Módulos Completos por Categoria de Ambiente")

    if "carrinho" not in st.session_state:
        st.session_state.carrinho = []
    if "modulo_temporario" not in st.session_state:
        st.session_state.modulo_temporario = None

    # BARRA LATERAL CUSTOS
    st.sidebar.header("💰 Custos e Margens")
    preco_chapa = st.sidebar.number_input("Preço Chapa MDF 15mm (R$)", value=280.0, step=10.0)
    preco_fita = st.sidebar.number_input("Preço Metro Fita (R$)", value=1.50, step=0.20)
    preco_corredica = st.sidebar.number_input("Preço Par Corrediças (R$)", value=25.0, step=5.0)
    preco_dobradica = st.sidebar.number_input("Preço Unidade Dobradiça (R$)", value=6.0, step=1.0)
    margem_lucro = st.sidebar.slider("Margem de Lucro (%)", min_value=50, max_value=300, value=100, step=10)

    aba_montar, aba_carrinho = st.tabs(["🛠️ Projetar Móvel", "🛒 Carrinho & Proposta"])

    with aba_montar:
        st.write("### 📝 Identificação")
        nome_cliente = st.text_input("Nome do Cliente / Ambiente", value="Cliente Padrão")

        st.write("### 📐 Medidas Gerais (mm)")
        col1, col2, col3 = st.columns(3)
        with col1: largura = st.number_input("Largura", value=1000, step=50)
        with col2: altura = st.number_input("Altura", value=800, step=50)
        with col3: profundidade = st.number_input("Profundidade", value=600, step=50)

        st.write("### 🏢 Categorias")
        ambiente = st.selectbox("Escolha o Ambiente:", ["🍳 Cozinha", "🧼 Banheiro / Lavanderia", "🛏️ Quarto / Closet", "📺 Sala de Estar"])
        
        if ambiente == "🍳 Cozinha":
            opcoes_moveis = ["Balcão de Pia (Portas)", "Gaveteiro de Cozinha", "Armário Aéreo", "Torre Quente (Paneleiro)", "Balcão de Canto L"]
        elif ambiente == "🧼 Banheiro / Lavanderia":
            opcoes_moveis = ["Gabinete de Banheiro (Suspenso)", "Armário Multiuso Alto", "Nicho Aberto Lavanderia"]
        elif ambiente == "🛏️ Quarto / Closet":
            opcoes_moveis = ["Módulo Closet Aberto", "Módulo Guarda-Roupas (Com Portas)", "Criado-Mudo"]
        else:
            opcoes_moveis = ["Rack de TV Baixo", "Painel de TV Traseiro", "Mesa de Centro", "Aéreo Decorativo Sala"]

        tipo_movel = st.selectbox("Selecione o Móvel Específico:", opcoes_moveis)
        movel = ModuloMarcenaria(largura, altura, profundidade)

        st.write("### 🔩 Configurações Internas e Ferragens")
        
        # Renderização dinâmica dos parâmetros baseado no móvel escolhido
        pecas = []
        qtd_c, qtd_d = 0, 0
        
        if tipo_movel in ["Balcão de Pia (Portas)", "Armário Aéreo", "Armário Multiuso Alto", "Módulo Guarda-Roupas (Com Portas)"]:
            p = st.number_input("Prateleiras", value=1, min_value=0)
            pt = st.number_input("Portas", value=2, min_value=0)
            if st.button("Gerar Estrutura", use_container_width=True):
                pecas = movel.calcular_caixaria() + movel.calcular_fundo() + movel.adicionar_prateleiras(p) + movel.calcular_portas_batentes(pt)
                qtd_d = pt * 2
                st.session_state.modulo_temporario = {"nome": f"{tipo_movel}", "pecas": pecas, "qtd_c": 0, "qtd_d": qtd_d}

        elif tipo_movel in ["Gaveteiro de Cozinha", "Gabinete de Banheiro (Suspenso)", "Criado-Mudo", "Rack de TV Baixo"]:
            g = st.number_input("Quantidade de Gavetas", value=3, min_value=1)
            if st.button("Gerar Estrutura", use_container_width=True):
                pecas = movel.calcular_caixaria() + movel.calcular_fundo() + movel.calcular_gavetas(g)
                qtd_c = g
                st.session_state.modulo_temporario = {"nome": f"{tipo_movel}", "pecas": pecas, "qtd_c": qtd_c, "qtd_d": 0}

        elif tipo_movel == "Torre Quente (Paneleiro)":
            p = st.number_input("Prateleiras Internas", value=2, min_value=0)
            pt = st.number_input("Portas (Superior/Inferior)", value=2, min_value=0)
            if st.button("Gerar Estrutura", use_container_width=True):
                pecas = movel.calcular_torre_quente(p, pt)
                qtd_d = pt * 2
                st.session_state.modulo_temporario = {"nome": f"{tipo_movel}", "pecas": pecas, "qtd_c": 0, "qtd_d": qtd_d}

        elif tipo_movel == "Balcão de Canto L":
            pt = st.number_input("Portas Articuladas", value=1, min_value=1)
            if st.button("Gerar Estrutura", use_container_width=True):
                pecas = movel.calcular_balcao_canto_l(pt)
                qtd_d = pt * 2 # Dobradiças especiais de canto
                st.session_state.modulo_temporario = {"nome": f"{tipo_movel}", "pecas": pecas, "qtd_c": 0, "qtd_d": qtd_d}

        elif tipo_movel == "Módulo Closet Aberto":
            p = st.number_input("Prateleiras/Colmeias", value=4, min_value=0)
            if st.button("Gerar Estrutura", use_container_width=True):
                pecas = movel.calcular_closet_aberto(p)
                st.session_state.modulo_temporario = {"nome": f"{tipo_movel}", "pecas": pecas, "qtd_c": 0, "qtd_d": 0}

        elif tipo_movel == "Painel de TV Traseiro":
            if st.button("Gerar Estrutura", use_container_width=True):
                pecas = movel.calcular_painel_tv()
                st.session_state.modulo_temporario = {"nome": f"{tipo_movel}", "pecas": pecas, "qtd_c": 0, "qtd_d": 0}

        elif tipo_movel == "Mesa de Centro":
            if st.button("Gerar Estrutura", use_container_width=True):
                pecas = movel.calcular_mesa_centro()
                st.session_state.modulo_temporario = {"nome": f"{tipo_movel}", "pecas": pecas, "qtd_c": 0, "qtd_d": 0}

        else: # Nicho Aberto Lavanderia / Aéreo Decorativo Sala
            p = st.number_input("Divisórias", value=0, min_value=0)
            if st.button("Gerar Estrutura", use_container_width=True):
                pecas = movel.calcular_caixaria() + movel.adicionar_prateleiras(p)
                st.session_state.modulo_temporario = {"nome": f"{tipo_movel}", "pecas": pecas, "qtd_c": 0, "qtd_d": 0}

        if st.session_state.modulo_temporario is not None:
            mod = st.session_state.modulo_temporario
            orcamento_modulo = movel.calcular_orcamento(mod["pecas"], preco_chapa, preco_fita, mod["qtd_c"], preco_corredica, mod["qtd_d"], preco_dobradica)
            
            st.info(f"⚡ Pronto: **{mod['nome']} ({largura}x{altura}x{profundidade}mm)**")
            if st.button("➕ ADICIONAR AO AMBIENTE", type="primary", use_container_width=True):
                st.session_state.carrinho.append({
                    "nome": f"{mod['nome']} ({largura}x{altura}x{profundidade}mm)",
                    "pecas": mod["pecas"],
                    "resumo": orcamento_modulo
                })
                st.session_state.modulo_temporario = None
                st.success("Adicionado com sucesso ao carrinho!")

    # ABA 2: CARRINHO E FECHAMENTO
    with aba_carrinho:
        st.write("## 🛒 Resumo do Ambiente")

        if st.session_state.carrinho:
            total_mdf, total_custo, total_venda = 0.0, 0.0, 0.0
            todas_as_pecas_consolidadas = []

            for idx, item in enumerate(st.session_state.carrinho):
                total_mdf += item['resumo']['area_mdf']
                total_custo += item['resumo']['custo_total']
                res = item['resumo']
                
                with st.expander(f"📦 Mód. {idx+1}: {item['nome']}"):
                    st.write(f"🪵 **MDF:** {res['area_mdf']:.2f}m² | 🎗️ **Fita:** {res['metros_fita']:.1f}m | 🔩 **Ferragem:** R${res['custo_ferragens']:.2f}")
                    
                    tabela_compacta = []
                    for p in item['pecas']:
                        tabela_compacta.append({
                            "Peça": p["Peça"], "Qtd": p["Quantidade"], "X(mm)": p["Dimensão X (mm)"], "Y(mm)": p["Dimensão Y (mm)"]
                        })
                    st.dataframe(tabela_compacta, use_container_width=True, hide_index=True)
                    
                for p in item['pecas']:
                    todas_as_pecas_consolidadas.append({
                        "Módulo": item['nome'], "Peça": p["Peça"], "Qtd": p["Quantidade"], "X": p["Dimensão X (mm)"], "Y": p["Dimensão Y (mm)"]
                    })

            multiplicador = 1 + (margem_lucro / 100.0)
            total_venda = total_custo * multiplicador

            st.divider()
            m_col1, m_col2, m_col3 = st.columns(3)
            with m_col1:
                st.metric("🪵 MDF Total necessário", f"{total_mdf:.2f} m²", f"~{round(total_mdf/5.06, 2)} Chapa(s)")
            with m_col2:
                st.metric("💵 Custo de Fabricação", f"R$ {total_custo:.2f}")
            with m_col3:
                st.metric("🎯 Preço Final Comercial", f"R$ {total_venda:.2f}")
            st.divider()

            st.write("### 📤 Fechamento")
            
            if st.button("💾 Salvar no Banco Histórico", use_container_width=True):
                salvar_no_banco(nome_cliente, st.session_state.carrinho, total_custo, total_venda)
                st.balloons()
                st.success("Gravado com sucesso!")

            output = io.StringIO()
            writer = csv.writer(output, delimiter=';', lineterminator='\n')
            writer.writerow(["Modulo", "Peca", "Quantidade", "X", "Y"])
            for p in todas_as_pecas_consolidadas:
                writer.writerow([p["Módulo"], p["Peça"], p["Qtd"], p["X"], p["Y"]])
            
            st.download_button("📥 Exportar Lista (Excel/CSV)", data=output.getvalue(), file_name="plano_corte.csv", mime="text/csv", use_container_width=True)

            # --- NOVO BLOCO DE PDF (CLIENTE VS LOJA) ---
            tipo_pdf = st.radio("Selecione o formato do PDF:", ["Cliente", "Loja"], horizontal=True)
            modo_geracao = "cliente" if tipo_pdf == "Cliente" else "loja"

            # Chamada da função com o novo parâmetro 'tipo_proposta'
            pdf_bytes = gerar_pdf_proposta(nome_cliente, st.session_state.carrinho, total_custo, total_venda, tipo_proposta=modo_geracao)
            
            st.download_button(
                label=f"📥 Baixar PDF ({tipo_pdf})",
                data=pdf_bytes,
                file_name=f"proposta_{modo_geracao}_{nome_cliente.replace(' ', '_').lower()}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

            st.write("")
            if st.button("🗑️ Limpar Todo o Ambiente", type="secondary", use_container_width=True):
                st.session_state.carrinho = []
                st.session_state.modulo_temporario = None
                st.rerun()
        else:
            st.warning("Nenhum móvel no ambiente. Monte um módulo na primeira aba!")