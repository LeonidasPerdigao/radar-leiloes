import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Radar de Leilões Brasil", layout="wide")

st.title("🚗 Analisador de Oportunidades em Leilões")
st.subheader("Simulação de Lucratividade e Análise de Risco")

# --- PAINEL LATERAL (ENTRADA DE DADOS) ---
st.sidebar.header("Dados do Veículo")
modelo = st.sidebar.text_input("Modelo do Carro", "Honda Civic 2020")
valor_fipe = st.sidebar.number_input("Valor de Tabela FIPE (R$)", min_value=1000, value=100000)
lance_vitoria = st.sidebar.number_input("Valor do seu Lance (R$)", min_value=1000, value=60000)
tipo_leilao = st.sidebar.selectbox("Tipo de Leilão", ["Recuperado de Financiamento", "Seguradora (Pequena Monta)", "Seguradora (Média Monta)"])

# --- LÓGICA DE CÁLCULO (O "CÉREBRO") ---
comissao_leiloeiro = lance_vitoria * 0.05
taxa_administrativa = 1500 # Média Brasil
logistica_est = 1200 # Guincho e transporte
custo_total = lance_vitoria + comissao_leiloeiro + taxa_administrativa + logistica_est

# Valor de revenda estimado (Carro de leilão perde 25% a 30% do valor de mercado)
valor_revenda_est = valor_fipe * 0.75
lucro_estimado = valor_revenda_est - custo_total
margem_percentual = (lucro_estimado / custo_total) * 100

# --- EXIBIÇÃO DOS RESULTADOS ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Custo Total (C/ Taxas)", f"R$ {custo_total:,.2f}")

with col2:
    color = "normal" if lucro_estimado > 5000 else "inverse"
    st.metric("Lucro Estimado na Revenda", f"R$ {lucro_estimado:,.2f}", delta=f"{margem_percentual:.1f}%")

with col3:
    if tipo_leilao == "Seguradora (Média Monta)":
        st.error("RISCO: ALTO (Dificuldade de Seguro/Revenda)")
    elif lucro_estimado < 2000:
        st.warning("RISCO: MARGEM BAIXA")
    else:
        st.success("OPORTUNIDADE: VERDE")

# --- TABELA DE DETALHAMENTO ---
st.write("---")
st.write("### Detalhamento Financeiro")
df_detalhes = pd.DataFrame({
    "Item": ["Lance", "Comissão (5%)", "Taxas Adm.", "Logística/Documento", "VALOR FINAL"],
    "Valor (R$)": [f"{lance_vitoria:,.2f}", f"{comissao_leiloeiro:,.2f}", f"{taxa_administrativa:,.2f}", f"{logistica_est:,.2f}", f"{custo_total:,.2f}"]
})
st.table(df_detalhes)

st.info("Nota: Este app é um simulador. Para integração em tempo real com leiloeiros, é necessário contratar uma API de dados (como CheckLeilão ou OlhoNoCarro).")
