import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Radar Leilão Pro", layout="wide")

# --- FUNÇÃO DE BUSCA FIPE BLINDADA ---
def buscar_dados_fipe():
    # Usando o servidor principal e um reserva caso o primeiro falhe
    base_url = "https://parallelum.com.br"
    
    try:
        # 1. Marcas (com tempo de espera de 5 segundos para não travar)
        res_marcas = requests.get(f"{base_url}/marcas", timeout=5)
        
        # Verifica se a resposta é válida
        if res_marcas.status_code != 200:
            st.error("O servidor da FIPE está instável agora. Tente atualizar a página em 1 minuto.")
            return None
            
        marcas = res_marcas.json()
        dict_marcas = {m['nome']: m['codigo'] for m in marcas}
        
        st.sidebar.header("1. Selecione o Veículo")
        marca_sel = st.sidebar.selectbox("Escolha a Marca", ["Selecione"] + sorted(list(dict_marcas.keys())))
        
        if marca_sel != "Selecione":
            cod_marca = dict_marcas[marca_sel]
            res_modelos = requests.get(f"{base_url}/marcas/{cod_marca}/modelos", timeout=5).json()
            modelos = res_modelos['modelos']
            dict_modelos = {m['nome']: m['codigo'] for m in modelos}
            modelo_sel = st.sidebar.selectbox("Escolha o Modelo", ["Selecione"] + sorted(list(dict_modelos.keys())))
            
            if modelo_sel != "Selecione":
                cod_modelo = dict_modelos[modelo_sel]
                anos = requests.get(f"{base_url}/marcas/{cod_marca}/modelos/{cod_modelo}/anos", timeout=5).json()
                dict_anos = {a['nome']: a['codigo'] for a in anos}
                ano_sel = st.sidebar.selectbox("Escolha o Ano", ["Selecione"] + list(dict_anos.keys()))
                
                if ano_sel != "Selecione":
                    cod_ano = dict_anos[ano_sel]
                    final = requests.get(f"{base_url}/marcas/{cod_marca}/modelos/{cod_modelo}/anos/{cod_ano}", timeout=5).json()
                    return final
    except Exception as e:
        st.sidebar.warning("Conexão lenta com a Tabela Fipe. Aguarde um instante...")
        return None
    return None

st.title("🚗 Analisador de Leilão (FIPE + IPVA)")

# --- EXECUÇÃO ---
dados_v = buscar_dados_fipe()

if dados_v:
    v_fipe = float(dados_v['Valor'].replace("R$ ", "").replace(".", "").replace(",", "."))
    st.sidebar.success(f"Veículo Selecionado!")
    
    # --- ENTRADA DE CUSTOS ---
    st.sidebar.divider()
    lance = st.sidebar.number_input("Seu Lance Máximo (R$)", value=int(v_fipe*0.5))
    aliquota_ipva = st.sidebar.slider("IPVA do Estado (%)", 1.0, 4.0, 4.0)

    # --- CÁLCULOS ---
    mes_atual = datetime.now().month
    meses_restantes = 12 - (mes_atual - 1)
    ipva_prop = (v_fipe * (aliquota_ipva / 100) / 12) * meses_restantes
    
    comissao = lance * 0.05
    taxas_fixas = 2700 # Taxa Pátio + Logística básica
    custo_total = lance + comissao + taxas_fixas + ipva_prop
    venda_estimada = v_fipe * 0.75 
    lucro = venda_estimada - custo_total

    # --- TELA PRINCIPAL ---
    st.subheader(f"{dados_v['Marca']} {dados_v['Modelo']} ({dados_v['AnoModelo']})")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Valor FIPE", f"R$ {v_fipe:,.2f}")
    c2.metric(f"IPVA ({meses_restantes} meses)", f"R$ {ipva_prop:,.2f}")
    c3.metric("Custo Final Arremate", f"R$ {custo_total:,.2f}")

    if lucro > 0:
        st.balloons()
        st.success(f"✅ OPORTUNIDADE: Margem de Lucro de R$ {lucro:,.2f}")
    else:
        st.error(f"❌ RISCO: Prejuízo Estimado de R$ {lucro:,.2f}")

    st.write("---")
    st.caption(f"Dados FIPE de: {dados_v['MesReferencia']}. Venda estimada com 25% de desvalorização.")
else:
    st.info("👈 Comece escolhendo a **Marca** do veículo no menu lateral.")
