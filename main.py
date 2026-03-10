import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time

st.set_page_config(layout="wide", page_title="Radar de Pressão Vando")

st.markdown("""
    <style>
    .main { background-color: #000000; }
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def buscar_pressao_noticia():
    try:
        data = yf.download('^GSPC', period="1d", interval="1m", progress=False)
        if not data.empty:
            abertura = data['Open'].iloc[0]
            serie_rastro = ((data['Close'] - abertura) / abertura) * 100
            valor_atual = serie_rastro.iloc[-1]
            return serie_rastro, valor_atual
    except:
        pass
    return pd.Series(), 0

rastro, pressao = buscar_pressao_noticia()

if not rastro.empty:
    fig = go.Figure()

    # LÓGICA DINÂMICA: As linhas se excitam com a pressão
    pos_vermelha = 0.80 if pressao > 0.15 else 0.45
    pos_verde = -0.80 if pressao < -0.15 else -0.45

    # 1. LINHA CINZA TRACEJADA (NEUTRA)
    fig.add_hline(y=0, line_dash="dash", line_color="grey", line_width=2, 
                 annotation_text="NEUTRO: SEM DIREÇÃO", annotation_position="top left")

    # 2. LINHA VERMELHA (OTIMISMO / PRESSÃO DE ALTA)
    fig.add_hline(y=pos_vermelha, line_color="red", line_width=4, 
                 annotation_text="OTIMISMO: PRESSÃO DE VENDA NO DÓLAR", annotation_position="top right")

    # 3. LINHA VERDE (PESSIMISMO / PRESSÃO DE BAIXA)
    fig.add_hline(y=pos_verde, line_color="green", line_width=4, 
                 annotation_text="PESSIMISMO: PRESSÃO DE COMPRA NO DÓLAR", annotation_position="bottom right")

    # 4. O RASTRO AZUL (TENDÊNCIA QUE BUSCA A PRESSÃO)
    fig.add_trace(go.Scatter(x=rastro.index, y=rastro, 
                             name="Rastro de Tendência", 
                             line=dict(color='deepskyblue', width=6, dash='dash')))

    fig.update_layout(
        title=f"RADAR VANDO - PRESSÃO ATUAL: {pressao:+.3f}%",
        template="plotly_dark",
        yaxis=dict(range=[-1.2, 1.2], gridcolor='#222'),
        height=700,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

time.sleep(60)
st.rerun()





