import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time

st.set_page_config(layout="wide", page_title="Radar Vando")
st.markdown("<style>.main {background-color: #000000;}</style>", unsafe_allow_html=True)

def buscar_dados():
    try:
        # Puxa 1 dia de dados com intervalo de 1 minuto
        df = yf.download('^GSPC', period="1d", interval="1m", progress=False)
        if not df.empty:
            abertura = df['Open'].iloc[0]
            # Calcula a variação real em porcentagem
            rastro_serie = ((df['Close'] - abertura) / abertura) * 100
            return rastro_serie, float(rastro_serie.iloc[-1])
    except:
        pass
    return pd.Series([0]), 0.0

rastro, pressao = buscar_dados()

st.title("RASTREADOR MÉTODO MACRO | VANDO MUNIZ")

if not rastro.empty:
    fig = go.Figure()

    # --- LÓGICA DINÂMICA DO VANDO (TROCA DE LUGAR) ---
    # Se Bolsa cai -> Compra Dólar (Verde no Topo)
    if pressao < -0.01:
        vde, cin, ver = 1.0, 0.5, 0.0
        sinal = "PESSIMISMO: COMPRA DÓLAR"
    # Se Bolsa sobe -> Venda Dólar (Vermelho no Topo)
    elif pressao > 0.01:
        ver, cin, vde = 1.0, 0.5, 0.0
        sinal = "OTIMISMO: VENDA DÓLAR"
    else:
        cin, ver, vde = 1.0, 0.5, 0.0
        sinal = "NEUTRO"

    # Linhas de Pressão Estilo Neon
    fig.add_hline(y=ver, line_color="red", line_width=10, annotation_text="VENDA DÓLAR", annotation_font_size=25)
    fig.add_hline(y=vde, line_color="green", line_width=10, annotation_text="COMPRA DÓLAR", annotation_font_size=25)
    fig.add_hline(y=cin, line_dash="dash", line_color="grey", line_width=3)

    # O Rastro Azul (Agora ele vai aparecer!)
    # Normalizamos o rastro para ele caber entre 0 e 1 e você ver a curva
    rastro_norm = (rastro - rastro.min()) / (rastro.max() - rastro.min() + 0.0001)
    
    fig.add_trace(go.Scatter(y=rastro_norm, mode='lines', 
                             line=dict(color='deepskyblue', width=12, dash='dash'),
                             name="Tendência"))

    fig.update_layout(
        title=dict(text=f"SINAL: {sinal} ({pressao:+.3f}%)", font=dict(size=30, color='white')),
        template="plotly_dark", plot_bgcolor='black', paper_bgcolor='black',
        yaxis=dict(range=[-0.2, 1.2], showticklabels=False, showgrid=False),
        height=800
    )
    st.plotly_chart(fig, use_container_width=True)

time.sleep(30)
st.rerun()




