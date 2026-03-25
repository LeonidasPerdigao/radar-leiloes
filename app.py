import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# Configuração da Página
st.set_page_config(page_title="Radar Leilão Pro", page_icon="🏎️", layout="wide")

# CSS para customização de Layout Moderno
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #eee;
    }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #1e293b; }
    .status-card {
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 25px;
        text-align: center;
        font-family: 'sans-serif';
    }
    .report-box {
        background-color: #f1f5f9;
        padding: 15px;
        border-radius: 10px;
        border: 1px dashed #cbd5e1;
        font-family: monospace;
    }
    </style>
    """, unsafe_allow_stdio=True)

# --- FUNÇÃO DE BUSCA FIPE ---
def buscar_dados_fipe():
    base_url = "https://parallelum.com.br"
    try:
        res_marcas = requests.get(base_url, timeout=5)
        if res_marcas.status_code != 200: return None
        marcas = res_marcas.json()
        dict_marcas = {m['nome']: m['codigo'] for m in marcas}
        
        st.sidebar.markdown("### 🔍 Veículo")
        marca_sel = st.sidebar.selectbox("Marca", ["Selecione"] + sorted(list(dict_marcas.keys())))
        
        if marca_sel != "Selecione":
            cod_marca = dict_marcas[marca_sel]
            modelos = requests.get(f"{base_url}/{cod_marca}/modelos", timeout=5).json()['modelos']
            dict_modelos = {m['nome']: m['codigo'] for m in modelos}
            modelo_sel = st.sidebar.selectbox("Modelo", ["Selecione"] + sorted(list(dict_modelos.keys())))
            
            if modelo_sel != "Selecione":
                cod_modelo = dict_modelos[modelo_sel]
                anos = requests.get(f"{base_url}/{cod_marca}/modelos/{cod_modelo}/anos", timeout=5).json()
                dict_anos = {a['nome']: a['codigo'] for a in anos}
                ano_sel = st.sidebar.selectbox("Ano", ["Selecione"] + list(dict_anos.keys()))
                
                if ano_sel != "Selecione":
                    return requests.get(f"{base_url}/{cod_marca}/modelos/{cod_modelo}/anos/{dict_anos[ano_sel]}", timeout=5).json()
    except: return None
    return None

# --- UI PRINCIPAL ---
st.markdown("# 🏎️ Radar de Leilões <span style='font-size: 0.5em; color: #64748b;'>v2.1</span>", unsafe_allow_stdio=True)

dados_v = buscar_dados_fipe()

if dados_v:
    v_fipe = float(dados_v['Valor'].replace("R$ ", "").replace(".", "").replace(",", "."))
    
    # Entradas na Barra Lateral
    st.sidebar.markdown("### 💰 Finanças")
    lance = st.sidebar.number_input("Seu Lance (R$)", value=int(v_fipe*0.5))
    aliquota_ipva = st.sidebar.slider("IPVA (%)", 1.0, 4.0, 4.0)
    taxas_extras = st.sidebar.number_input("Consertos/Pátio/Docs (R$)", value=3500)

    # Cálculos
    mes_atual = datetime.now().month
    meses_restantes = 12 - (mes_atual - 1)
    ipva_prop = (v_fipe * (aliquota_ipva / 100) / 12) * meses_restantes
    comissao = lance * 0.05
    custo_total = lance + comissao + taxas_extras + ipva_prop
    venda_estimada = v_fipe * 0.75 # Padrão leilão: 25% desc.
    lucro = venda_estimada - custo_total
    roi = (lucro / custo_total) * 100 if custo_total > 0 else 0

    # Dashboard de Métricas
    st.subheader(f"{dados_v['Marca']} {dados_v['Modelo']} {dados_v['AnoModelo']}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tabela FIPE", f"R$ {v_fipe:,.0f}")
    c2.metric("IPVA ({meses_restantes}m)", f"R$ {ipva_prop:,.0f}")
    c3.metric("Investimento", f"R$ {custo_total:,.0f}")
    c4.metric("ROI Est.", f"{roi:.1f}%")

    # Card de Status
    if lucro > 0:
        st.markdown(f"""<div style='background-color: #dcfce7; border: 1px solid #22c55e;' class='status-card'>
            <h2 style='color: #166534; margin:0;'>✅ OPORTUNIDADE</h2>
            <p style='color: #166534; font-size:1.2rem;'>Lucro líquido estimado: <b>R$ {lucro:,.2f}</b></p>
        </div>""", unsafe_allow_stdio=True)
    else:
        st.markdown(f"""<div style='background-color: #fee2e2; border: 1px solid #ef4444;' class='status-card'>
            <h2 style='color: #991b1b; margin:0;'>⚠️ ALTO RISCO</h2>
            <p style='color: #991b1b; font-size:1.2rem;'>Prejuízo estimado: <b>R$ {abs(lucro):,.2f}</b></p>
        </div>""", unsafe_allow_stdio=True)

    # RELATÓRIO PARA WHATSAPP
    st.markdown("### 📲 Compartilhar Análise")
    texto_whats = f"""*RELATÓRIO DE LEILÃO* 🏎️
---
*Veículo:* {dados_v['Marca']} {dados_v['Modelo']}
*Ano:* {dados_v['AnoModelo']}
---
📊 *DADOS FINANCEIROS:*
• Tabela FIPE: R$ {v_fipe:,.2f}
• Lance Proposto: R$ {lance:,.2f}
• IPVA Proporcional: R$ {ipva_prop:,.2f}
• Custos (Comissão/Docs/Pátio): R$ {(comissao + taxas_extras):,.2f}

💰 *INVESTIMENTO TOTAL:* R$ {custo_total:,.2f}
📈 *LUCRO ESTIMADO:* R$ {lucro:,.2f}
🎯 *RETORNO (ROI):* {roi:.1f}%

_Análise gerada via Radar Leilão Pro_"""

    with st.expander("Gerar texto para WhatsApp"):
        st.info("Copie o texto abaixo e cole no seu WhatsApp:")
        st.code(texto_whats, language="text")

    # Detalhamento
    with st.expander("📄 Ver Planilha de Custos"):
        df_detalhes = pd.DataFrame({
            "Descrição": ["Lance Base", "Comissão (5%)", "Taxas/Pátio/Consertos", "IPVA Proporcional", "TOTAL"],
            "Valor": [f"R$ {lance:,.2f}", f"R$ {comissao:,.2f}", f"R$ {taxas_extras:,.2f}", f"R$ {ipva_prop:,.2f}", f"R$ {custo_total:,.2f}"]
        })
        st.table(df_detalhes)

else:
    st.info("👈 Selecione o veículo no menu lateral para iniciar.")

st.sidebar.markdown("---")
st.sidebar.caption(f"FIPE Ref: {datetime.now().strftime('%m/%Y')}")
