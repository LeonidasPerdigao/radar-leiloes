import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Radar Leilão Pro", layout="wide")

# --- FUNÇÃO DE BUSCA FIPE MELHORADA ---
def buscar_dados_fipe():
    base_url = "https://parallelum.com.br"
    
    # 1. Marcas
    res_marcas = requests.get(base_url)
    if res_marcas.status_code != 200:
        st.error("Erro ao conectar com o servidor da FIPE. Tente atualizar a página.")
        return None
    
    marcas = res_marcas.json()
    dict_marcas = {m['nome']: m['codigo'] for m in marcas}
    marca_sel = st.sidebar.selectbox("1. Escolha a Marca", ["Selecione"] + list(dict_marcas.keys()))
    
    if marca_sel != "Selecione":
        # 2. Modelos
        cod_marca = dict_marcas[marca_sel]
        modelos = requests.get(f"{base_url}/{cod_marca}/modelos").json()['modelos']
        dict_modelos = {m['nome']: m['codigo'] for m in modelos}
        modelo_sel = st.sidebar.selectbox("2. Escolha o Modelo", ["Selecione"] + list(dict_modelos.keys()))
        
        if modelo_sel != "Selecione":
            # 3. Anos
            cod_modelo = dict_modelos[modelo_sel]
            anos = requests.get(f"{base_url}/{cod_marca}/modelos/{cod_modelo}/anos").json()
            dict_anos = {a['nome']: a['codigo'] for a in anos}
            ano_sel = st.sidebar.selectbox("3. Escolha o Ano", ["Selecione"] + list(dict_anos.keys()))
            
            if ano_sel != "Selecione":
                cod_ano = dict_anos[ano_sel]
                final = requests.get(f"{base_url}/{cod_marca}/modelos/{cod_modelo}/anos/{cod_ano}").json()
                return final
    return None

st.title("🚗 Analisador de Leilão (FIPE + IPVA)")

# --- EXECUÇÃO ---
st.sidebar.header("Busca Automática")
dados_v = buscar_dados_fipe()

if dados_v:
    v_fipe = float(dados_v['Valor'].replace("R$ ", "").replace(".", "").replace(",", "."))
    st.sidebar.success(f"Veículo: {dados_v['Modelo']}")
    st.sidebar.info(f"FIPE: {dados_v['Valor']}")
    
    # --- ENTRADA DE CUSTOS ---
    st.sidebar.divider()
    lance = st.sidebar.number_input("Seu Lance (R$)", value=int(v_fipe*0.5))
    aliquota_ipva = st.sidebar.slider("IPVA do Estado (%)", 1.0, 4.0, 4.0)

    # --- CÁLCULOS ---
    mes_atual = datetime.now().month
    meses_restantes = 12 - (mes_atual - 1)
    ipva_prop = (v_fipe * (aliquota_ipva / 100) / 12) * meses_restantes
    
    comissao = lance * 0.05
    taxas_fixas = 2700 # Taxa Pátio + Logística básica
    custo_total = lance + comissao + taxas_fixas + ipva_prop
    venda_estimada = v_fipe * 0.75 # 25% abaixo da FIPE por ser leilão
    lucro = venda_estimada - custo_total

    # --- TELA PRINCIPAL ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Valor FIPE", f"R$ {v_fipe:,.2f}")
    c2.metric("IPVA ({meses_restantes} meses)", f"R$ {ipva_prop:,.2f}")
    c3.metric("Custo Total", f"R$ {custo_total:,.2f}")

    if lucro > 0:
        st.balloons()
        st.success(f"💰 Margem de Lucro: R$ {lucro:,.2f}")
    else:
        st.error(f"📉 Prejuízo Estimado: R$ {lucro:,.2f}")
else:
    st.warning("👈 Use o menu ao lado para selecionar um veículo e começar a análise.")
