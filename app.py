import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Radar Leilão Pro", layout="wide")

# --- FUNÇÃO DE BUSCA FIPE ---
def buscar_fipe(tipo="carros"):
    base_url = "https://parallelum.com.br"
    
    # Busca Marcas
    marcas = requests.get(f"{base_url}/{tipo}/marcas").json()
    dict_marcas = {m['nome']: m['codigo'] for m in marcas}
    marca_sel = st.sidebar.selectbox("Escolha a Marca", list(dict_marcas.keys()))
    
    # Busca Modelos
    modelos = requests.get(f"{base_url}/{tipo}/marcas/{dict_marcas[marca_sel]}/modelos").json()
    dict_modelos = {m['nome']: m['codigo'] for m in modelos['modelos']}
    modelo_sel = st.sidebar.selectbox("Escolha o Modelo", list(dict_modelos.keys()))
    
    # Busca Anos
    anos = requests.get(f"{base_url}/{tipo}/marcas/{dict_marcas[marca_sel]}/modelos/{dict_modelos[modelo_sel]}/anos").json()
    dict_anos = {a['nome']: a['codigo'] for a in anos}
    ano_sel = st.sidebar.selectbox("Ano do Veículo", list(dict_anos.keys()))
    
    dados = requests.get(f"{base_url}/{tipo}/marcas/{dict_marcas[marca_sel]}/modelos/{dict_modelos[modelo_sel]}/anos/{dict_anos[ano_sel]}").json()
    return dados

st.title("🚗 Analisador de Leilão com FIPE e IPVA")

# --- LÓGICA DE DADOS ---
st.sidebar.header("1. Consultar Veículo")
try:
    dados_v = buscar_fipe()
    v_fipe = float(dados_v['Valor'].replace("R$ ", "").replace(".", "").replace(",", "."))
    st.sidebar.success(f"Valor FIPE: {dados_v['Valor']}")
except:
    st.sidebar.warning("Aguardando seleção do veículo...")
    v_fipe = 0

st.sidebar.header("2. Custos do Leilão")
lance = st.sidebar.number_input("Seu Lance (R$)", value=int(v_fipe*0.5) if v_fipe > 0 else 10000)
aliquota_ipva = st.sidebar.slider("Alíquota IPVA do Estado (%)", 1.0, 4.0, 4.0) # 4% é o padrão SP/RJ/MG

# --- CÁLCULO IPVA PROPORCIONAL ---
mes_atual = datetime.now().month
meses_restantes = 12 - (mes_atual - 1) # Calcula do mês atual até dezembro
ipva_total = v_fipe * (aliquota_ipva / 100)
ipva_proporcional = (ipva_total / 12) * meses_restantes

# --- CUSTOS TOTAIS ---
comissao = lance * 0.05
taxa_adm = 1500
logistica = 1200
custo_total = lance + comissao + taxa_adm + logistica + ipva_proporcional

# Margem de Revenda (Carro de leilão = FIPE - 25%)
venda_est = v_fipe * 0.75
lucro = venda_est - custo_total

# --- PAINEL DE RESULTADOS ---
c1, c2, c3 = st.columns(3)
c1.metric("Valor FIPE", f"R$ {v_fipe:,.2f}")
c2.metric("IPVA Proporcional", f"R$ {ipva_proporcional:,.2f}", f"{meses_restantes} meses")
c3.metric("Custo Total Arremate", f"R$ {custo_total:,.2f}")

st.divider()

if lucro > 0:
    st.balloons()
    st.success(f"💰 Lucro Estimado de R$ {lucro:,.2f} na revenda!")
else:
    st.error(f"📉 Prejuízo Estimado de R$ {lucro:,.2f}. Lance muito alto!")

st.write("### Resumo de Despesas")
df = pd.DataFrame({
    "Despesa": ["Lance", "Comissão (5%)", "Taxa Pátio", "Logística", "IPVA Proporcional"],
    "Valor (R$)": [f"R$ {lance:,.2f}", f"R$ {comissao:,.2f}", f"R$ {taxa_adm:,.2f}", f"R$ {logistica:,.2f}", f"R$ {ipva_proporcional:,.2f}"]
})
st.table(df)
