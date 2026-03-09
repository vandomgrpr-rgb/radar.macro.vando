import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf

# Configuração da página para o estilo Trader profissional
st.set_page_config(page_title="Radar Macro Vando", layout="wide")

def buscar_dados():
    # Tickers públicos e gratuitos do Yahoo Finance
    tickers = {'SPY': 'S&P 500', 'DX-Y.NYB': 'DXY', 'DI=F': 'DI Futuro'}
    dados = {}
    for t in tickers:
        try:
            ticker = yf.Ticker(t)
            hist = ticker.history(period="2d")
            if not hist.empty and len(hist) >= 2:
                fech_atual = hist['Close'].iloc[-1]
                fech_ant = hist['Close'].iloc[-2]
                pct = ((fech_atual - fech_ant) / fech_ant) * 100
                dados[t] = pct
            else:
                dados[t] = 0.0
        except Exception:
            dados[t] = 0.0 # Se falhar, coloca 0 em vez de dar erro vermelho
    return dados

st.title("RASTREADOR MÉTODO MACRO | VANDO MUNIZ")

precos = buscar_dados()

# Criando o gráfico com as LINHAS GROSSAS que você queria
fig = go.Figure()

# Montando o visual do radar
indices = ['S&P 500', 'DXY', 'DI Futuro']
valores = [precos.get('SPY', 0), precos.get('DX-Y.NYB', 0), precos.get('DI=F', 0)]

fig.add_trace(go.Scatter(
    x=indices, 
    y=valores,
    mode='lines+markers+text',
    line=dict(color='lime', width=8), # LINHA SUPER GROSSA E NEON
    marker=dict(size=15, color='white'),
    text=[f"{v:.2f}%" for v in valores],
    textposition="top center"
))

fig.update_layout(
    template="plotly_dark",
    plot_bgcolor='black',
    paper_bgcolor='black',
    height=600,
    yaxis=dict(title="Variação %", gridcolor='gray'),
    xaxis=dict(gridcolor='gray')
)

st.plotly_chart(fig, use_container_width=True)

