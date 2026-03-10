from flask import Flask
import yfinance as yf
import os

app = Flask(_name) # Corrigido aqui: __name_ com dois sublinhados

def calcular_rastro():
    try:
        # Ibovespa, Dólar, S&P 500 Futuro, Petróleo Brent
        tickers = ["^BVSP", "BRL=X", "ES=F", "BZ=F"]
        data = yf.download(tickers, period="1d", interval="5m", progress=False)['Close']
        
        if data.empty:
            return None

        atual = data.iloc[-1]
        abertura = data.iloc[0]
        
        v_ibov = ((atual['^BVSP'] / abertura['^BVSP']) - 1) * 100
        v_dolar = ((atual['BRL=X'] / abertura['BRL=X']) - 1) * 100
        v_sp = ((atual['ES=F'] / abertura['ES=F']) - 1) * 100
        v_pet = ((atual['BZ=F'] / abertura['BZ=F']) - 1) * 100

        # Score do Vando (Foco B3)
        score = (v_ibov * 0.6) - (v_dolar * 0.4) + (v_sp * 0.1) - (v_pet * 0.1)
        
        return {
            "score": round(score, 3),
            "ibov": round(v_ibov, 2),
            "dolar": round(v_dolar, 2),
            "pet": round(v_pet, 2)
        }
    except:
        return None

@app.route('/')
def home():
    res = calcular_rastro()
    if not res:
        return "<body style='background:black;color:white;'><h1>Carregando dados do mercado...</h1><script>setTimeout(function(){location.reload();}, 5000);</script></body>"
    
    cor = "green" if res['score'] > 0 else "red"
    
    return f"""
    <body style="background-color: black; color: white; font-family: sans-serif; text-align: center; padding-top: 50px;">
        <h1 style="font-size: 40px;">RASTRO DO MERCADO</h1>
        <div style="font-size: 100px; color: {cor}; font-weight: bold;">{res['score']}%</div>
        <hr style="width: 50%; margin: 30px auto;">
        <div style="font-size: 25px;">
            <p>IBOVESPA: {res['ibov']}% | DÓLAR: {res['dolar']}%</p>
            <p>PETRÓLEO BRENT: {res['pet']}%</p>
        </div>
        <p style="color: gray;">Atualiza sozinho a cada 2 min</p>
        <script>setTimeout(function(){{ location.reload(); }}, 120000);</script>
    </body>
    """

if _name_ == "_main_":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)





