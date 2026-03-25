import streamlit as st
import pandas as pd

st.set_page_config(page_title="Radar de Leilões Pro", layout="wide")

st.title("📊 Calculadora de Viabilidade de Leilão")

# --- ENTRADA DE DADOS ---
st.sidebar.header("1. Dados do Arremate")
modelo = st.sidebar.text_input("Modelo", "Ex: Corolla 2022")
valor_fipe = st.sidebar.number_input("Valor FIPE Atual (R$)", value=80000)
lance_proposto = st.sidebar.number_input("Seu Lance Máximo (R$)", value=45000)

st.sidebar.header("2. Taxas e Logística")
porte_veiculo = st.sidebar.selectbox("Porte do Veículo", ["Pequeno (Motos/Hatch)", "Médio (Sedan/SUV)", "Grande (Caminhonete/Van)"])
distancia_km = st.sidebar.number_input("Distância do Pátio (KM)", value=100)
custo_km = st.sidebar.slider("Valor do Guincho por KM (R$)", 2.5, 10.0, 4.5)

# --- LÓGICA DE CÁLCULO AJUSTADA ---
# Taxa administrativa média por porte
taxas_por_porte = {"Pequeno (Motos/Hatch)": 900, "Médio (Sedan/SUV)": 1600, "Grande (Caminhonete/Van)": 2400}
taxa_adm_fixa = taxas_por_porte[porte_veiculo]

comissao_leiloeiro = lance_proposto * 0.05
icms_estatutario = lance_proposto * 0.009 # Média de 0.9% cobrada em editais
frete_total = distancia_km * custo_km
documentacao_est = 1200 # Transferência + taxas Detran

custo_total = lance_proposto + comissao_leiloeiro + taxa_adm_fixa + icms_estatutario + frete_total + documentacao_est

# Cálculo de Margem Realista (Carro de leilão vende com 20% a 30% de desconto)
valor_venda_alvo = valor_fipe * 0.80 
lucro_liquido = valor_venda_alvo - custo_total
roi = (lucro_liquido / custo_total) * 100

# --- EXIBIÇÃO ---
c1, c2, c3 = st.columns(3)
c1.metric("Custo Final", f"R$ {custo_total:,.2f}")
c2.metric("Lucro Líquido Est.", f"R$ {lucro_liquido:,.2f}")
c3.metric("ROI (Retorno)", f"{roi:.1f}%")

if lucro_liquido > 8000:
    st.success("✅ OPORTUNIDADE REAL: Margem de lucro segura.")
elif lucro_liquido > 0:
    st.warning("⚠️ ATENÇÃO: Margem apertada. Qualquer conserto extra tira o lucro.")
else:
    st.error("❌ PREJUÍZO: O custo total supera o valor de revenda de leilão.")

st.write("### Detalhamento dos Custos Ocultos")
tabela = pd.DataFrame({
    "Descrição": ["Lance Base", "Comissão Leiloeiro (5%)", "Taxa Adm. Pátio", "ICMS/Taxas Editais", "Guincho/Logística", "Docs/Detran"],
    "Valor": [lance_proposto, comissao_leiloeiro, taxa_adm_fixa, icms_estatutario, frete_total, documentacao_est]
})
st.table(tabela.assign(Valor=tabela['Valor'].map('R$ {:,.2f}'.format)))
