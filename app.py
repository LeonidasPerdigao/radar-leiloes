import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# Configuração da Página
st.set_page_config(page_title="Radar Leilão Pro", page_icon="🏎️", layout="wide")

# --- CSS CORRIGIDO (Dando vida ao layout moderno) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }
    .status-card {
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
        text-align: center;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

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
st.markdown("# 🏎️ Radar de Leilões <span style='font-size: 0.5em; color: #64748b;'>v2.2</span>", unsafe_allow_html=True)

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
    venda_estimada = v_fipe * 0.75 
    lucro = venda_estimada - custo_total
    roi = (lucro / custo_total) * 100 if custo_total > 0 else 0

    # Dashboard de Métricas
    st.subheader(f"{dados_v['Marca']} {dados_v['Modelo']} {dados_v['AnoModelo']}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tabela FIPE", f"R$ {v_fipe:,.0f}")
    c2.metric(f"IPVA ({meses_restantes}m)", f"R$ {ipva_prop:,.0f}")
    c3.metric("Investimento", f"R$ {custo_total:,.0f}")
    c4.metric("ROI Est.", f"{roi:.1f}%")

    # Card de Status
    if lucro > 0:
        st.markdown(f"<div style='background-color: #dcfce7; color: #166534;' class='status-card'>✅ OPORTUNIDADE: Lucro Estimado de R$ {lucro:,.2f}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='background-color: #fee2e2; color: #991b1b;' class='status-card'>⚠️ RISCO: Prejuízo Estimado de R$ {abs(lucro):,.2f}</div>", unsafe_allow_html=True)

    # RELATÓRIO PARA WHATSAPP
    st.markdown("### 📲 Compartilhar Análise")
    texto_whats = f"*RELATÓRIO DE LEILÃO*\n\n*Veículo:* {dados_v['Marca']} {dados_v['Modelo']}\n*FIPE:* R$ {v_fipe:,.2f}\n*Lance:* R$ {lance:,.2f}\n*Investimento:* R$ {custo_total:,.2f}\n*Lucro Est.:* R$ {lucro:,.2f}\n*ROI:* {roi:.1f}%"
    
    with st.expander("Gerar texto para WhatsApp"):
        st.code(texto_whats, language="text")

else:
    st.info("👈 Selecione o veículo no menu lateral para iniciar.")
