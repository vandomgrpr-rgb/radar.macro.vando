import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf

# Configuração da página para o estilo Trader
st.set_page_config(page_title="Radar Macro Vando", layout="wide")

def buscar_dados():
    tickers = {'SPY': 'S&P 500', 'DI=F': 'DI Futuro', 'DX-Y.NYB': 'DXY'}
    dados = {}
    for t in tickers:
        try:
            ticker = yf.Ticker(t)
            hist = ticker.history(period="2d")
            if not hist.empty:
                fech_atual = hist['Close'].iloc[-1]
                fech_ant = hist['Close'].iloc[-2]
                pct = ((fech_atual - fech_ant) / fech_ant) * 100
                dados[t] = pct
            else:
                dados[t] = 0.0
        except:
            dados[t] = 0.0
    return dados

st.title("RASTREADOR MÉTODO MACRO | VANDO MUNIZ")

precos = buscar_dados()

# Criando o gráfico com linhas GROSSAS e NEON
fig = go.Figure()

# Exemplo de linha para o radar
fig.add_trace(go.Scatter(
    x=['DXY', 'S&P 500', 'DI'], 
    y=[precos.get('DX-Y.NYB', 0), precos.get('SPY', 0), precos.get('DI=F', 0)],
    mode='lines+markers+text',
    line=dict(color='lime', width=6), # LINHA BEM GROSSA
    marker=dict(size=12, color='white'),
    textposition="top center"
))

fig.update_layout(
    template="plotly_dark",
    plot_bgcolor='black',
    paper_bgcolor='black',
    height=600
)

st.plotly_chart(fig, use_container_width=True)
