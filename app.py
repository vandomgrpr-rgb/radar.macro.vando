import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta, timezone
import requests
import warnings
import time

warnings.filterwarnings("ignore")

# CONFIGURAÇÃO - COLE SUA CHAVE AQUI
ALPHA_VANTAGE_API_KEY = "JBIJLOP76X2DOLBQ"  # ← SUBSTITUA

# CACHE GLOBAL
CACHE = {
    'df': None,
    'ultimo_sucesso': None,
    'yahoo_falhou': False,
    'alpha_count': 0,
    'ultima_req_alpha': None
}

app = dash.Dash(__name__)
server = app.server

TICKERS_YAHOO = {
    'IBOV': '^BVSP', 
    'SP500': '^GSPC', 
    'DOLAR': 'BRL=X', 
    'MXN': 'MXN=X'
}

# Mapeamento para Alpha Vantage (símbolos diferentes)
TICKERS_ALPHA = {
    'IBOV': 'IBOV.SAO',      # Ibovespa
    'SP500': 'SPY',          # ETF do S&P500 (mais líquido)
    'DOLAR': 'BRLUSD',       # USD/BRL
    'MXN': 'MXNUSD'          # USD/MXN
}

app.layout = html.Div([
    html.Div([
        html.H1("MÉTODO MASTER", style={
            'color': '#00bcff',
            'textAlign': 'center',
            'margin': '10px',
            'fontFamily': 'Arial, sans-serif',
            'fontSize': '24px'
        }),
        html.Div(id='score-display', style={
            'textAlign': 'center',
            'fontSize': '32px',
            'fontWeight': 'bold',
            'margin': '10px',
            'fontFamily': 'Arial, sans-serif'
        }),
        html.Div(id='timestamp', style={
            'textAlign': 'center',
            'color': '#888',
            'fontSize': '14px',
            'marginBottom': '10px'
        }),
        html.Div(id='status-msg', style={
            'textAlign': 'center',
            'fontSize': '11px',
            'marginBottom': '20px',
            'fontFamily': 'monospace'
        })
    ]),
    
    dcc.Graph(
        id='grafico-principal',
        config={'displayModeBar': False},
        style={'height': '70vh'}
    ),
    
    # Intervalo: 10 minutos (economiza requisições)
    dcc.Interval(
        id='interval-component',
        interval=600*1000,  # 10 minutos
        n_intervals=0
    )
], style={
    'backgroundColor': 'black',
    'minHeight': '100vh',
    'padding': '20px'
})

def fetch_alpha_vantage():
    """Busca dados da Alpha Vantage (usa apenas se Yahoo falhar)"""
    global CACHE
    
    # Verifica limite diário
    hoje = datetime.now(timezone.utc).date()
    if CACHE['ultima_req_alpha'] and CACHE['ultima_req_alpha'].date() == hoje:
        if CACHE['alpha_count'] >= 25:
            return None, "Limite Alpha Vantage atingido (25/dia)"
    else:
        # Novo dia, reseta contador
        CACHE['alpha_count'] = 0
        CACHE['ultima_req_alpha'] = datetime.now(timezone.utc)
    
    data_frames = {}
    
    try:
        for nome, symbol in TICKERS_ALPHA.items():
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={ALPHA_VANTAGE_API_KEY}&outputsize=compact"
            
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if "Time Series (5min)" in data:
                df = pd.DataFrame.from_dict(data["Time Series (5min)"], orient='index')
                df = df.rename(columns={
                    '1. open': 'Open',
                    '2. high': 'High', 
                    '3. low': 'Low',
                    '4. close': 'Close',
                    '5. volume': 'Volume'
                })
                df.index = pd.to_datetime(df.index)
                df = df.sort_index()
                df = df.astype(float)
                
                if not df.empty:
                    abertura = df['Open'].iloc[0]
                    df['Variacao'] = ((df['Close'] - abertura) / abertura) * 100
                    data_frames[nome] = df['Variacao']
                
                CACHE['alpha_count'] += 1
                time.sleep(0.5)  # Respeita rate limit
            
            elif "Note" in data:
                return None, f"Limite API atingido: {data['Note']}"
            elif "Information" in data:
                return None, f"Erro API: {data['Information']}"
                
        if len(data_frames) >= 2:  # Pelo menos 2 tickers
            df_final = pd.DataFrame(data_frames).dropna()
            if not df_final.empty:
                return process_data(df_final), "ALPHA VANTAGE"
        
        return None, "Dados insuficientes Alpha Vantage"
        
    except Exception as e:
        return None, f"Erro Alpha Vantage: {str(e)}"

def fetch_yahoo():
    """Busca dados do Yahoo Finance"""
    data_frames = {}
    
    try:
        for nome, ticker in TICKERS_YAHOO.items():
            time.sleep(0.3)  # Delay para não sobrecarregar
            df = yf.download(ticker, period='1d', interval='5m', progress=False)
            
            if not df.empty and len(df) > 0:
                abertura = df['Open'].iloc[0]
                df['Variacao'] = ((df['Close'] - abertura) / abertura) * 100
                data_frames[nome] = df['Variacao']
        
        if len(data_frames) >= 4:
            df_final = pd.DataFrame(data_frames).dropna()
            if not df_final.empty:
                return process_data(df_final), "YAHOO FINANCE"
        
        return None, "Yahoo incompleto"
        
    except Exception as e:
        return None, f"Yahoo erro: {str(e)}"

def process_data(df):
    """Processa DataFrame com as linhas do método"""
    df['VERDE'] = (df['IBOV'] + df['SP500']) / 2
    df['VERMELHA'] = (df['DOLAR'] + df['MXN']) / 2
    df['RASTRO_AZUL'] = df['VERDE'] - df['VERMELHA']
    df['CINZA_NEUTRA'] = 0
    return df

def fetch_data():
    """Estratégia híbrida: Yahoo primeiro, Alpha como backup"""
    global CACHE
    
    # 1. Tenta Yahoo Finance (gratuito)
    df, fonte = fetch_yahoo()
    
    if df is not None:
        CACHE['df'] = df.copy()
        CACHE['ultimo_sucesso'] = datetime.now(timezone.utc)
        CACHE['yahoo_falhou'] = False
        return df, f"ONLINE • {fonte}", "#00ff00"
    
    # 2. Yahoo falhou, tenta Alpha Vantage (25 req/dia)
    if not CACHE['yahoo_falhou']:
        print("Yahoo falhou, tentando Alpha Vantage...")
        CACHE['yahoo_falhou'] = True
    
    df, fonte = fetch_alpha_vantage()
    
    if df is not None:
        CACHE['df'] = df.copy()
        CACHE['ultimo_sucesso'] = datetime.now(timezone.utc)
        return df, f"ONLINE • {fonte} ({CACHE['alpha_count']}/25)", "#00ff00"
    
    # 3. Ambos falharam, usa cache
    if CACHE['df'] is not None:
        minutos = (datetime.now(timezone.utc) - CACHE['ultimo_sucesso']).seconds // 60
        return CACHE['df'], f"OFFLINE • Cache ({minutos}min) • Alpha usada: {CACHE['alpha_count']}/25", "#ffaa00"
    
    return None, "SEM DADOS • Verifique conexão", "#ff0000"

@app.callback(
    [Output('grafico-principal', 'figure'),
     Output('score-display', 'children'),
     Output('score-display', 'style'),
     Output('timestamp', 'children'),
     Output('status-msg', 'children'),
     Output('status-msg', 'style')],
    [Input('interval-component', 'n_intervals')]
)
def update_graph(n):
    df_final, status_msg, status_color = fetch_data()
    
    # Hora de Brasília
    agora_utc = datetime.now(timezone.utc)
    agora_brasilia = agora_utc - timedelta(hours=3)
    hora_str = f"Atualizado: {agora_brasilia.strftime('%H:%M:%S')} (Brasília)"
    
    status_style = {'color': status_color, 'textAlign': 'center'}
    
    if df_final is None:
        fig = go.Figure()
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='black',
            plot_bgcolor='black',
            height=600,
            annotations=[{
                'text': 'Aguardando dados do mercado...',
                'xref': 'paper',
                'yref': 'paper',
                'showarrow': False,
                'font': {'size': 20, 'color': '#666'}
            }]
        )
        return fig, "Carregando...", {'color': '#888', 'textAlign': 'center', 'fontSize': '32px'}, hora_str, status_msg, status_style
    
    # Gráfico
    score_atual = df_final['RASTRO_AZUL'].iloc[-1]
    cor_score = "#00ff00" if score_atual > 0 else "#ff0000"
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_final.index, y=df_final['CINZA_NEUTRA'], name='NEUTRO', line=dict(color='gray', width=2, dash='dash')))
    fig.add_trace(go.Scatter(x=df_final.index, y=df_final['VERMELHA'], name='VERMELHA', line=dict(color='#ff0000', width=3)))
    fig.add_trace(go.Scatter(x=df_final.index, y=df_final['VERDE'], name='VERDE', line=dict(color='#00ff00', width=3)))
    fig.add_trace(go.Scatter(x=df_final.index, y=df_final['RASTRO_AZUL'], name='RASTRO', line=dict(color='#00bcff', width=6, dash='dot')))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='black',
        plot_bgcolor='black',
        height=600,
        margin=dict(l=5, r=40, t=10, b=20),
        yaxis=dict(gridcolor='#222', side="right", tickfont=dict(size=12), autorange=True),
        xaxis=dict(gridcolor='#222', tickfont=dict(size=11)),
        showlegend=False,
        dragmode=False
    )
    
    score_text = f"SCORE: {score_atual:.2f}"
    score_style = {'color': cor_score, 'textAlign': 'center', 'fontSize': '32px', 'fontWeight': 'bold'}
    
    return fig, score_text, score_style, hora_str, status_msg, status_style

if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=8050)












