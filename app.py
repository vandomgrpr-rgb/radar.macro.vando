import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta, timezone
import warnings

warnings.filterwarnings("ignore")

app = dash.Dash(__name__)
server = app.server  # CRÍTICO para gunicorn

TICKERS = {
    'IBOV': '^BVSP', 
    'SP500': '^GSPC', 
    'DOLAR': 'BRL=X', 
    'MXN': 'MXN=X'
}

app.layout = html.Div([
    html.H1("MÉTODO MASTER", style={
        'color': '#00bcff',
        'textAlign': 'center',
        'margin': '10px'
    }),
    html.Div(id='score-display', style={
        'textAlign': 'center',
        'fontSize': '32px',
        'fontWeight': 'bold'
    }),
    html.Div(id='timestamp', style={
        'textAlign': 'center',
        'color': '#888',
        'fontSize': '14px'
    }),
    dcc.Graph(id='grafico-principal', style={'height': '70vh'}),
    dcc.Interval(id='interval-component', interval=600000, n_intervals=0)
], style={
    'backgroundColor': 'black',
    'minHeight': '100vh',
    'padding': '20px'
})

def fetch_data():
    try:
        data_frames = {}
        for nome, ticker in TICKERS.items():
            df = yf.download(ticker, period='1d', interval='5m', progress=False)
            if not df.empty:
                abertura = df['Open'].iloc[0]
                df['Variacao'] = ((df['Close'] - abertura) / abertura) * 100
                data_frames[nome] = df['Variacao']
        
        if not data_frames:
            return None
            
        df_final = pd.DataFrame(data_frames).dropna()
        
        # Converte para horário de Brasília (UTC-3)
        df_final.index = df_final.index - timedelta(hours=3)
        
        df_final['VERDE'] = (df_final['IBOV'] + df_final['SP500']) / 2
        df_final['VERMELHA'] = (df_final['DOLAR'] + df_final['MXN']) / 2
        df_final['RASTRO_AZUL'] = df_final['VERDE'] - df_final['VERMELHA']
        df_final['CINZA_NEUTRA'] = 0
        
        return df_final
    except Exception as e:
        print(f"Erro: {e}")
        return None

@app.callback(
    [Output('grafico-principal', 'figure'),
     Output('score-display', 'children'),
     Output('score-display', 'style'),
     Output('timestamp', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_graph(n):
    df = fetch_data()
    
    agora = datetime.now(timezone.utc) - timedelta(hours=3)
    hora_str = agora.strftime('%H:%M:%S')
    
    if df is None or df.empty:
        fig = go.Figure()
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='black',
            plot_bgcolor='black',
            height=600
        )
        return fig, "Sem dados", {'color': '#ff6666', 'textAlign': 'center'}, f"Tentativa: {hora_str}"
    
    score = df['RASTRO_AZUL'].iloc[-1]
    cor_score = "#00ff00" if score > 0 else "#ff0000"
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index, 
        y=df['CINZA_NEUTRA'], 
        line=dict(color='gray', width=2, dash='dash'),
        name='NEUTRO'
    ))
    fig.add_trace(go.Scatter(
        x=df.index, 
        y=df['VERMELHA'], 
        line=dict(color='#ff0000', width=3),
        name='VERMELHA'
    ))
    fig.add_trace(go.Scatter(
        x=df.index, 
        y=df['VERDE'], 
        line=dict(color='#00ff00', width=3),
        name='VERDE'
    ))
    fig.add_trace(go.Scatter(
        x=df.index, 
        y=df['RASTRO_AZUL'], 
        line=dict(color='#00bcff', width=6, dash='dot'),
        name='RASTRO'
    ))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='black',
        plot_bgcolor='black',
        height=600,
        margin=dict(l=5, r=40, t=10, b=20),
        yaxis=dict(gridcolor='#222', side="right"),
        xaxis=dict(
            gridcolor='#222',
            tickformat='%H:%M',
            title='Horário (Brasília UTC-3)'
        ),
        showlegend=False
    )
    
    return fig, f"SCORE: {score:.2f}", {
        'color': cor_score, 
        'textAlign': 'center', 
        'fontSize': '32px',
        'fontWeight': 'bold'
    }, f"Atualizado: {hora_str}"

if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=8050)







