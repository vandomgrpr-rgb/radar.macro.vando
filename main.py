import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time

# Configuração de página
st.set_page_config(layout="wide", page_title="Radar Vando Muniz")

st.markdown("<style>.main {background-color: #000000;}</style>", unsafe_allow_html=True)

def buscar_dados():
    try:
        # Puxamos o S&P 500 para medir o sentimento global
        df = yf.download('^GSPC', period="1d", interval="1m", progress=False)
        if not df.empty:
            abertura = df['Open'].iloc[0]
            # Calculamos o rastro
            rastro_serie = ((df['Close'] - abertura) / abertura) * 100
            # Pegamos o ÚLTIMO valor real (garante que seja um número único)
            valor_atual = float(rastro_serie.iloc[-1])
            return rastro_serie, valor_atual
    except:
        pass
    return pd.Series(), 0.0

rastro, pressao = buscar_dados()

st.title("RASTREADOR MÉTODO MACRO | VANDO MUNIZ")

if not rastro.empty:
    fig = go.Figure()

    # --- LÓGICA DE POSIÇÃO DINÂMICA (TROCA DE LUGAR) ---
    # Se mercado cai (Pessimismo), Verde vai para o TOPO (Compra Dólar)
    if pressao < -0.05:
        pos_verde, pos_cinza, pos_vermelha = 1.0, 0.5, 0.0
        msg = "PESSIMISMO: COMPRA DÓLAR"
    # Se mercado sobe (Otimismo), Vermelha vai para o TOPO (Venda Dólar)
    elif pressao > 0.05:
        pos_vermelha, pos_cinza, pos_verde = 1.0, 0.5, 0.0
        msg = "OTIMISMO: VENDA DÓLAR"
    else:
        pos_cinza, pos_vermelha, pos_verde = 1.0, 0.5, 0.0
        msg = "NEUTRO: SEM LADO"

    # 1. LINHA VERMELHA
    fig.add_hline(y=pos_vermelha, line_color="red", line_width=6, 
                 annotation_text="VENDA DÓLAR", annotation_position="top right")

    # 2. LINHA VERDE
    fig.add_hline(y=pos_verde, line_color="green", line_width=6, 
                 annotation_text="COMPRA DÓLAR", annotation_position="bottom right")

    # 3. LINHA CINZA (NEUTRA)
    fig.add_hline(y=pos_cinza, line_dash="dash", line_color="grey", line_width=2)

    # 4. O RASTRO AZUL (MOVE-SE CONFORME O PREÇO)
    fig.add_trace(go.Scatter(y=rastro.values, mode='lines',
                             line=dict(color='deepskyblue', width=8, dash='dash'),
                             name="Tendência Real"))

    fig.update_layout(
        title=f"SENTIMENTO: {msg} ({pressao:+.3f}%)",
        template="plotly_dark", plot_bgcolor='black', paper_bgcolor='black',
        yaxis=dict(range=[-0.5, 1.5], showticklabels=False, gridcolor='#222'),
        height=700
    )
    st.plotly_chart(fig, use_container_width=True)

# Atualiza a cada 30 segundos
time.sleep(30)
st.rerun()





