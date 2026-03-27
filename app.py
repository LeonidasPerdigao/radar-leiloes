import streamlit as st
import pandas as pd

st.set_page_config(page_title="Radar Leilão", page_icon="🏎️", layout="wide")

st.title("🏎️ Radar de Leilões")

MARCAS = {
    "Fiat": ["Uno", "Strada", "Argo", "Cronos", "Mobi", "Palio", "Pulse"],
    "Volkswagen": ["Gol", "Voyage", "Polo", "Virtus", "Tiguan", "T-Cross"],
    "Chevrolet": ["Onix", "Tracker", "Cruze", "Equinox", "Montana", "Celta"],
    "Ford": ["Ka", "Fiesta", "Focus", "Fusion", "Ecosport", "Territory"],
    "Toyota": ["Corolla", "Etios", "Yaris", "Hilux", "RAV4", "Camry"],
    "Honda": ["City", "Civic", "HR-V", "CR-V", "Accord", "Fit"],
    "Hyundai": ["HB20", "I30", "Creta", "Tucson", "Santa Fe", "Venue"],
    "Kia": ["Cerato", "Picanto", "Sorento", "Sportage", "Niro", "Carens"],
}

ANOS = ["2024", "2023", "2022", "2021", "2020", "2019", "2018", "2017", "2016"]

st.write("### 🔍 1. Selecione o Veículo")
col1, col2, col3 = st.columns(3)

with col1:
    marca = st.selectbox("Marca", ["Selecione"] + list(MARCAS.keys()))

with col2:
    modelos = MARCAS.get(marca, ["Selecione"])
    modelo = st.selectbox("Modelo", ["Selecione"] + modelos if marca != "Selecione" else ["Selecione"])

with col3:
    ano = st.selectbox("Ano", ["Selecione"] + ANOS)

if marca == "Selecione" or modelo == "Selecione" or ano == "Selecione":
    st.stop()

st.write("### 💰 2. Análise")
ano_num = int(ano)
valor_base = 50000
depreciacao = (2024 - ano_num) * 0.08
valor_fipe = valor_base * (1 - depreciacao)

col1, col2 = st.columns(2)
with col1:
    st.metric("Valor FIPE", f"R$ {valor_fipe:,.2f}")
with col2:
    lance = st.number_input("Seu Lance (R$)", value=int(valor_fipe * 0.5), step=1000, min_value=1000)

taxa = lance * 0.05
taxa_fixa = 3500
ipva = (valor_fipe * 0.04 / 12) * 10
total = lance + taxa + taxa_fixa + ipva
revenda = valor_fipe * 0.75
lucro = revenda - total

st.markdown("---")
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Investimento", f"R$ {total:,.2f}")
with m2:
    st.metric("Revenda (75%)", f"R$ {revenda:,.2f}")
with m3:
    cor = "🟢" if lucro > 0 else "🔴"
    st.metric(f"{cor} Lucro", f"R$ {lucro:,.2f}")
with m4:
    if lucro > 0:
        roi = (lucro / total) * 100
        st.metric("ROI", f"{roi:.1f}%")

st.markdown("---")
st.write("### 📋 Custos")
df = pd.DataFrame([
    {"Item": "Lance", "Valor": f"R$ {lance:,.2f}"},
    {"Item": "Taxa (5%)", "Valor": f"R$ {taxa:,.2f}"},
    {"Item": "Taxa Fixa", "Valor": f"R$ {taxa_fixa:,.2f}"},
    {"Item": "IPVA", "Valor": f"R$ {ipva:,.2f}"},
])
st.dataframe(df, use_container_width=True, hide_index=True)
st.metric("TOTAL", f"R$ {total:,.2f}")

st.markdown("---")
if lucro > 0:
    st.success(f"✅ Viável! Lucro: R$ {lucro:,.2f}")
else:
    st.error(f"❌ Inviável! Prejuízo: R$ {abs(lucro):,.2f}")
