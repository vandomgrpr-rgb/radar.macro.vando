from flask import Flask
import yfinance as yf
import os

# ATENÇÃO: Os dois sublinhados antes e depois de name são OBRIGATÓRIOS
app = Flask(_name_)

def calcular_rastro_vando():
    try:
        # Puxando o que você pediu: IBOV, Dólar, Petróleo e S&P
        tickers = ["^BVSP", "BRL=X", "ES=F", "BZ=F"]
        data = yf.download(tickers, period="1d", interval="5m", progress=False)['Close']
        
        if data.empty:
            return None

        # Dados em tempo real vs abertura
        atual = data.iloc[-1]
        abertura = data.iloc[0]
        
        v_ibov = ((atual['^BVSP'] / abertura['^BVSP']) - 1) * 100
        v_dolar = ((atual['BRL=X'] / abertura['BRL=X']) - 1) * 100
        v_sp = ((atual['ES=F'] / abertura['ES=F']) - 1) * 100
        v_pet = ((atual['BZ=F'] / abertura['BZ=F']) - 1) * 100

        # O CÁLCULO (Se o Índice derrete e o Dólar sobe, o Score cai)
        score = (v_ibov * 0.6) - (v_dolar * 0.4) + (v_sp * 0.1) - (v_pet * 0.1)
        
        return {"score": round(score, 3), "ibov": round(v_ibov, 2), "dolar": round(v_dolar, 2), "pet": round(v_pet, 2)}
    except:
        return None

@app.route('/')
def home():
    res = calcular_rastro_vando()
    if not res:
        return "<body style='background:black;color:white;'><h1>Carregando mercado...</h1><script>setTimeout(function(){location.reload();}, 10000);</script></body>"
    
    cor = "green" if res['score'] > 0 else "red"
    
    return f"""
    <body style="background-color: black; color: white; font-family: sans-serif; text-align: center; padding-top: 50px;">
        <h1 style="font-size: 50px;">RASTRO DO MERCADO</h1>
        <div style="font-size: 150px; color: {cor}; font-weight: bold;">{res['score']}</div>
        <div style="font-size: 30px; margin-top: 20px;">
            <p>IBOVESPA: {res['ibov']}% | DÓLAR: {res['dolar']}%</p>
            <p>PETRÓLEO: {res['pet']}%</p>
        </div>
        <script>setTimeout(function(){{ location.reload(); }}, 300000);</script>
    </body>
    """

if _name_ == "_main_":
    # O Render exige que a gente pegue a porta do sistema
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)





