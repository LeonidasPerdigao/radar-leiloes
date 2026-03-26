import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Radar Leilão Pro", page_icon="🏎️", layout="wide")

# Função para buscar dados com tratamento de erro visual
def buscar_dados_fipe():
    base_url = "https://parallelum.com.br"
    try:
        # Tenta buscar as marcas
        res = requests.get(base_url, timeout=10)
        if res.status_code != 200:
            st.error("O servidor da FIPE não respondeu. Tente atualizar a página (F5).")
            return None
        
        marcas = res.json()
        dict_marcas = {m['nome']: m['codigo'] for m in marcas}
        
        # Colocamos os seletores na tela PRINCIPAL para você ver se funciona
        st.write("### 🔍 1. Escolha o Veículo")
        col_m, col_mod, col_ano = st.columns(3)
        
        with col_m:
            marca_sel = st.selectbox("Marca", ["Selecione"] + sorted(list(dict_marcas.keys())))
        
        if marca_sel != "Selecione":
            cod_m = dict_marcas[marca_sel]
            with col_mod:
                modelos = requests.get(f"{base_url}/{cod_m}/modelos", timeout=10).json()['modelos']
                dict_mod = {m['nome']: m['codigo'] for m in modelos}
                mod_sel = st.selectbox("Modelo", ["Selecione"] + sorted(list(dict_mod.keys())))
            
            if mod_sel != "Selecione":
                cod_mod = dict_mod[mod_sel]
                with col_ano:
                    anos = requests.get(f"{base_url}/{cod_m}/modelos/{cod_mod}/anos", timeout=10).json()
                    dict_anos = {a['nome']: a['codigo'] for a in anos}
                    ano_sel = st.selectbox("Ano", ["Selecione"] + list(dict_anos.keys()))
                
                if ano_sel != "Selecione":
                    return requests.get(f"{base_url}/{cod_m}/modelos/{cod_mod}/anos/{dict_anos[ano_sel]}", timeout=10).json()
    except Exception as e:
        st.warning(f"Erro de Conexão: Certifique-se de que o arquivo 'requirements.txt' tem a palavra 'requests'.")
        return None
    return None

# --- UI PRINCIPAL ---
st.markdown("# 🏎️ Radar de Leilões v2.3")
st.divider()

dados_v = buscar_dados_fipe()

if dados_v:
    v_fipe = float(dados_v['Valor'].replace("R$ ", "").replace(".", "").replace(",", "."))
    
    st.sidebar.header("💰 Configurações")
    lance = st.sidebar.number_input("Seu Lance (R$)", value=int(v_fipe*0.5))
    taxas = st.sidebar.number_input("Consertos/Pátio (R$)", value=3500)
    
    # Cálculos Simples
    mes_atual = datetime.now().month
    meses_rest = 12 - (mes_atual - 1)
    ipva = (v_fipe * 0.04 / 12) * meses_rest
    custo_total = lance + (lance * 0.05) + taxas + ipva
    lucro = (v_fipe * 0.75) - custo_total

    # Dashboard
    st.success(f"### Análise: {dados_v['Modelo']} ({dados_v['AnoModelo']})")
    c1, c2, c3 = st.columns(3)
    c1.metric("Valor FIPE", f"R$ {v_fipe:,.2f}")
    c2.metric("Investimento Total", f"R$ {custo_total:,.2f}")
    c3.metric("Lucro Estimado", f"R$ {lucro:,.2f}")
else:
    st.info("Aguardando você selecionar a **Marca** acima para carregar os dados...")
