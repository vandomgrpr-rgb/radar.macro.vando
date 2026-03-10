from flask import Flask
import yfinance as yf
import os

app = Flask(__name__)

def calcular_rastro():
    try:
        # Puxando Ibovespa, Dólar, S&P 500 Futuro e Petróleo Brent
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

        # PESOS DO VANDO (Radar 12)
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
        return "<body style='background:black;color:white;text-align:center;'><h1>Carregando mercado...</h1><script>setTimeout(function(){location.reload();}, 10000);</script></body>"
    
    cor_score = "green" if res['score'] > 0 else "red"
    
    return f"""
    <body style="background-color: black; color: white; font-family: sans-serif; text-align: center; padding-top: 50px;">
        <h1 style="font-size: 40px; margin-bottom: 5px;">RASTRO DO MERCADO</h1>
        <p style="color: gray; font-size: 18px;">Radar 12 - Vando Muniz</p>
        
        <div style="font-size: 180px; color: {cor_score}; font-weight: bold; margin: 30px 0;">
            {res['score']}
        </div>
        
        <div style="font-size: 32px; border-top: 1px solid #333; padding-top: 20px; display: inline-block; width: 85%;">
            <p>IBOVESPA: <b>{res['ibov']}%</b> | DÓLAR: <b>{res['dolar']}%</b></p>
            <p>PETRÓLEO BRENT: <b>{res['pet']}%</b></p>
        </div>
        
        <p style="color: #444; margin-top: 40px;">Atualização automática: 2 min</p>
        <script>setTimeout(function(){{ location.reload(); }}, 120000);</script>
    </body>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)









