import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime

# Configuração da Página
st.set_page_config(page_title="RASTREADOR MACRO - VANDO MUNIZ", layout="wide")
st.markdown("<style>body {background-color: #000000; color: white;}</style>", unsafe_allow_html=True)

# Título Profissional
st.title("📊 RASTREADOR MÉTODO MACRO | VANDO MUNIZ")

# Chave e Ativos (Ajustados para a lógica do Elton)
API_KEY = "SUA_CHAVE_AQUI"
# SPY representa o Otimismo (Linha Vermelha) | UUP representa o Pessimismo (Linha Verde)
symbols = "SPY,UUP"

def buscar_dados():
    url = f"https://api.twelvedata.com/quote?symbol={symbols}&apikey={API_KEY}"
    res = requests.get(url).json()
    # No seu setup: Vermelha = Otimismo (Bolsas), Verde = Pessimismo (Dólar Global)
    otimismo = float(res['SPY']['percent_change'])
    pessimismo = float(res['UUP']['percent_change'])
    return otimismo, pessimismo

# Inicializando histórico no estado da sessão do navegador
if 'historico' not in st.session_state:
    st.session_state.historico = pd.DataFrame(columns=['Otimismo', 'Pessimismo', 'Gatilho', 'Neutro'])

# Busca de dados
otim, pess = buscar_dados()
gatilho = otim - pess
novo_dado = {'Otimismo': otim, 'Pessimismo': pess, 'Gatilho': gatilho, 'Neutro': 0}
st.session_state.historico = pd.concat([st.session_state.historico, pd.DataFrame([novo_dado])]).tail(50)

# --- CRIAÇÃO DO GRÁFICO PROFISSIONAL ---
fig = go.Figure()

# Linha Vermelha (Otimismo/Bolsas) - Grossa
fig.add_trace(go.Scatter(y=st.session_state.historico['Otimismo'], name='OTIMISMO (BOLSAS)',
                         line=dict(color='#FF0000', width=5)))

# Linha Verde (Pessimismo) - Grossa
fig.add_trace(go.Scatter(y=st.session_state.historico['Pessimismo'], name='PESSIMISMO (MEDO)',
                         line=dict(color='#00FF00', width=5)))

# Linha Cinza (Neutro) - Tracejada
fig.add_trace(go.Scatter(y=st.session_state.historico['Neutro'], name='NEUTRO',
                         line=dict(color='#808080', width=2, dash='dash')))

# Linha Azul (Gatilho/Pressão) - Tracejada
fig.add_trace(go.Scatter(y=st.session_state.historico['Gatilho'], name='GATILHO AZUL (PRESSÃO)',
                         line=dict(color='#00D9FF', width=3, dash='dot')))

# Ajustes de Layout (Estilo Dark Terminal)
fig.update_layout(
    plot_bgcolor='black', paper_bgcolor='black',
    font_color='white', height=600,
    xaxis=dict(showgrid=False),
    yaxis=dict(gridcolor='#222222', zeroline=False),
    margin=dict(l=20, r=20, t=20, b=20)
)

st.plotly_chart(fig, use_container_width=True)

# Painel de Decisão
st.markdown("---")
col1, col2 = st.columns(2)
if otim > pess:
    col1.error(f"🚨 SENTIDO: VENDA DÓLAR (Otimismo no Topo)")
else:
    col1.success(f"🚨 SENTIDO: COMPRA DÓLAR (Pessimismo no Topo)")

col2.info(f"⏱️ ÚLTIMA ATUALIZAÇÃO: {datetime.now().strftime('%H:%M:%S')}")