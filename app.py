import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Radar Leilão Pro", page_icon="🏎️", layout="wide")

# Função com endereço reserva (Plano B)
def buscar_dados_fipe():
    # Tentamos o endereço principal primeiro
    urls = [
        "https://parallelum.com.br",
        "https://fipe.parallelum.com.br" # Servidor reserva
    ]
    
    res = None
    for url in urls:
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                break
        except:
            continue
            
    if not res or res.status_code != 200:
        st.error("Servidor da FIPE ocupado. Aguarde 30 segundos e clique em 'Tentar Novamente'.")
        if st.button("Tentar Novamente"):
            st.rerun()
        return None

    marcas = res.json()
    dict_marcas = {m['nome']: m['codigo'] for m in marcas}
    
    st.write("### 🔍 1. Escolha o Veículo")
    col_m, col_mod, col_ano = st.columns(3)
    
    with col_m:
        marca_sel = st.selectbox("Marca", ["Selecione"] + sorted(list(dict_marcas.keys())))
    
    if marca_sel != "Selecione":
        cod_m = dict_marcas[marca_sel]
        # Busca modelos no mesmo servidor que funcionou
        base = url.replace("/marcas", "")
        modelos_res = requests.get(f"{base}/marcas/{cod_m}/modelos").json()
        dict_mod = {m['nome']: m['codigo'] for m in modelos_res['modelos']}
        
        with col_mod:
            mod_sel = st.selectbox("Modelo", ["Selecione"] + sorted(list(dict_mod.keys())))
        
        if mod_sel != "Selecione":
            cod_mod = dict_mod[mod_sel]
            anos = requests.get(f"{base}/marcas/{cod_m}/modelos/{cod_mod}/anos").json()
            dict_anos = {a['nome']: a['codigo'] for a in anos}
            
            with col_ano:
                ano_sel = st.selectbox("Ano", ["Selecione"] + list(dict_anos.keys()))
            
            if ano_sel != "Selecione":
                return requests.get(f"{base}/marcas/{cod_m}/modelos/{cod_mod}/anos/{dict_anos[ano_sel]}").json()
    return None

# --- RESTO DO APP ---
st.markdown("# 🏎️ Radar de Leilões")
dados_v = buscar_dados_fipe()

if dados_v:
    v_fipe = float(dados_v['Valor'].replace("R$ ", "").replace(".", "").replace(",", "."))
    st.sidebar.success(f"FIPE: {dados_v['Valor']}")
    lance = st.sidebar.number_input("Seu Lance (R$)", value=int(v_fipe*0.5))
    
    # Cálculo IPVA Proporcional Março/2026
    mes_rest = 10 # Março a Dezembro
    ipva = (v_fipe * 0.04 / 12) * mes_rest
    total = lance + (lance * 0.05) + 3500 + ipva
    lucro = (v_fipe * 0.75) - total

    c1, c2, c3 = st.columns(3)
    c1.metric("Valor FIPE", f"R$ {v_fipe:,.2f}")
    c2.metric("Investimento", f"R$ {total:,.2f}")
    c3.metric("Lucro Est.", f"R$ {lucro:,.2f}")
else:
    st.info("Aguardando seleção da marca acima...")
