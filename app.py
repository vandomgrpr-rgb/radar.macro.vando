import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta, timezone
import warnings

warnings.filterwarnings("ignore")

# Inicializa o app Dash
app = dash.Dash(__name__)
server = app.server  # Necessário para o Render/Gunicorn

# Configuração dos tickers
TICKERS = {
    'IBOV': '^BVSP', 
    'SP500': '^GSPC', 
    'DOLAR': 'BRL=X', 
    'MXN': 'MXN=X'
}

# Layout do dashboard
app.layout = html.Div([
    # Header com Score
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
            'marginBottom': '20px'
        })
    ]),
    
    # Gráfico
    dcc.Graph(
        id='grafico-principal',
        config={'displayModeBar': False},
        style={'height': '70vh'}
    ),
    
    # Intervalo de atualização (60 segundos)
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # 60 segundos em milissegundos
        n_intervals=0
    )
], style={
    'backgroundColor': 'black',
    'minHeight': '100vh',
    'padding': '20px'
})

def fetch_data():
    """Busca dados do Yahoo Finance"""
    data_frames = {}
    
    try:
        for nome, ticker in TICKERS.items():
            df = yf.download(ticker, period='1d', interval='5m', progress=False)
            if not df.empty:
                abertura = df['Open'].iloc[0]
                df['Variacao'] = ((df['Close'] - abertura) / abertura) * 100
                data_frames[nome] = df['Variacao']
        
        df_final = pd.DataFrame(data_frames).dropna()
        df_final['VERDE'] = (df_final['IBOV'] + df_final['SP500']) / 2
        df_final['VERMELHA'] = (df_final['DOLAR'] + df_final['MXN']) / 2
        df_final['RASTRO_AZUL'] = df_final['VERDE'] - df_final['VERMELHA']
        df_final['CINZA_NEUTRA'] = 0
        
        return df_final
    except Exception as e:
        print(f"Erro ao buscar dados: {e}")
        return None

@app.callback(
    [Output('grafico-principal', 'figure'),
     Output('score-display', 'children'),
     Output('score-display', 'style'),
     Output('timestamp', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_graph(n):
    df_final = fetch_data()
    
    if df_final is None or df_final.empty:
        # Retorna gráfico vazio em caso de erro
        fig = go.Figure()
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='black',
            plot_bgcolor='black'
        )
        return fig, "Erro ao carregar dados", {'color': 'orange', 'textAlign': 'center'}, ""
    
    # Calcula score atual
    score_atual = df_final['RASTRO_AZUL'].iloc[-1]
    cor_score = "#00ff00" if score_atual > 0 else "#ff0000"
    
    # Cria o gráfico
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_final.index, 
        y=df_final['CINZA_NEUTRA'], 
        name='NEUTRO', 
        line=dict(color='gray', width=2, dash='dash')
    ))
    
    fig.add_trace(go.Scatter(
        x=df_final.index, 
        y=df_final['VERMELHA'], 
        name='VERMELHA', 
        line=dict(color='#ff0000', width=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=df_final.index, 
        y=df_final['VERDE'], 
        name='VERDE', 
        line=dict(color='#00ff00', width=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=df_final.index, 
        y=df_final['RASTRO_AZUL'], 
        name='RASTRO', 
        line=dict(color='#00bcff', width=6, dash='dot')
    ))
    
    # Layout do gráfico
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='black',
        plot_bgcolor='black',
        height=600,
        margin=dict(l=5, r=40, t=10, b=20),
        yaxis=dict(
            gridcolor='#222', 
            side="right", 
            tickfont=dict(size=12), 
            autorange=True
        ),
        xaxis=dict(
            gridcolor='#222', 
            tickfont=dict(size=11)
        ),
        showlegend=False,
        dragmode=False
    )
    
    # Formata o display do score
    score_text = f"SCORE: {score_atual:.2f}"
    score_style = {
        'color': cor_score,
        'textAlign': 'center',
        'fontSize': '32px',
        'fontWeight': 'bold'
    }
    
    # HORÁRIO DE BRASÍLIA (UTC-3)
    agora_utc = datetime.now(timezone.utc)
    agora_brasilia = agora_utc - timedelta(hours=3)
    timestamp_text = f"Atualizado em: {agora_brasilia.strftime('%H:%M:%S')} (Brasília)"
    
    return fig, score_text, score_style, timestamp_text

if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=8050)











