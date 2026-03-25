import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Radar FIPE & Leilão", layout="wide")

# --- FUNÇÃO PARA BUSCAR DADOS DA FIPE (API GRATUITA) ---
def buscar_fipe(tipo="carros"):
    base_url = "https://parallelum.com.br"
    
    # 1. Buscar Marcas
    marcas = requests.get(f"{base_url}/{tipo}/marcas").json()
    dict_marcas = {m['nome']: m['codigo'] for m in marcas}
    marca_sel = st.sidebar.selectbox("Marca", list(dict_marcas.keys()))
    
    # 2. Buscar Modelos
    modelos = requests.get(f"{base_url}/{tipo}/marcas/{dict_marcas[marca_sel]}/modelos").json()
    dict_modelos = {m['nome']: m['codigo'] for m in modelos['modelos']}
    modelo_sel = st.sidebar.selectbox("Modelo", list(dict_modelos.keys()))
    
    # 3. Buscar Anos
    anos = requests.get(f"{base_url}/{tipo}/marcas/{dict_marcas[marca_sel]}/modelos/{dict_modelos[modelo_sel]}/anos").json()
    dict_anos = {a['nome']: a['codigo'] for a in anos}
    ano_sel = st.sidebar.selectbox("Ano Modelo", list(dict_anos.keys()))
    
    # 4. Pegar Valor Final
    dados_finais = requests.get(f"{base_url}/{tipo}/marcas/{dict_marcas[marca_sel]}/modelos/{dict_modelos[modelo_sel]}/anos/{dict_anos[ano_sel]}").json()
    return dados_finais

st.title("🚗 Analisador Automático: FIPE + Leilão")

# --- SIDEBAR COM INTEGRAÇÃO FIPE ---
st.sidebar.header("1. Seleção Automática FIPE")
try:
    dados_veiculo = buscar_fipe()
    valor_fipe_texto = dados_veiculo['Valor'] # Ex: "R$ 50.000,00"
    valor_fipe = float(valor_fipe_texto.replace("R$ ", "").replace(".", "").replace(",", "."))
    
    st.sidebar.success(f"FIPE Atualizada: {valor_fipe_texto}")
    st.sidebar.caption(f"Referência: {dados_veiculo['MesReferencia']}")
except:
    st.sidebar.error("Erro ao conectar com a FIPE. Tente novamente.")
    valor_fipe = 0

st.sidebar.header("2. Dados do Leilão")
lance_proposto = st.sidebar.number_input("Seu Lance (R$)", value=int(valor_fipe * 0.5) if valor_fipe > 0 else 10000)

# --- CÁLCULOS FINANCEIROS (Taxas Reais Brasil) ---
comissao_leiloeiro = lance_proposto * 0.05
taxa_adm = 1500 # Média Brasil
doc_logistica = 2200 # Documentos + Frete médio
custo_total = lance_proposto + comissao_leiloeiro + taxa_adm + doc_logistica

# Margem de Segurança: Carro de leilão vende 25% ABAIXO da FIPE
valor_venda_realista = valor_fipe * 0.75
lucro_estimado = valor_venda_realista - custo_total

# --- EXIBIÇÃO ---
col1, col2, col3 = st.columns(3)
col1.metric("Valor FIPE (Mercado)", f"R$ {valor_fipe:,.2f}")
col2.metric("Custo Total Arremate", f"R$ {custo_total:,.2f}")
col3.metric("Lucro Est. na Revenda", f"R$ {lucro_estimado:,.2f}")

if lucro_estimado > (valor_fipe * 0.1):
    st.balloons()
    st.success(f"🎯 EXCELENTE NEGÓCIO! Margem de {((lucro_estimado/custo_total)*100):.1f}%")
elif lucro_estimado > 0:
    st.warning("⚠️ CUIDADO: Margem muito apertada.")
else:
    st.error("❌ PREJUÍZO: O custo total supera o valor de revenda de leilão.")

st.info(f"O cálculo considera que você venderá o carro por **R$ {valor_venda_realista:,.2f}** (25% abaixo da FIPE), que é o padrão para veículos com passagem por leilão.")
