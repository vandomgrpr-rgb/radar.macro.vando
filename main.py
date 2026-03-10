from flask import Flask
import yfinance as yf

app = Flask(_name_)

def calcular_rastro():
    try:
        # Ibovespa, Dólar, S&P 500 Futuro, Petróleo Brent
        tickers = ["^BVSP", "BRL=X", "ES=F", "BZ=F"]
        data = yf.download(tickers, period="1d", interval="5m", progress=False)['Close']
        
        if data.empty:
            return "Aguardando sinal do mercado..."

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
        return "<h1>Erro na leitura dos dados. Tentando reconectar...</h1>"
    
    # Define a cor baseada no Score
    cor = "green" if res['score'] > 0 else "red"
    
    # HTML simples para aparecer na TV
    return f"""
    <body style="background-color: black; color: white; font-family: sans-serif; text-align: center; padding-top: 50px;">
        <h1 style="font-size: 60px;">RASTRO DO MERCADO</h1>
        <div style="font-size: 120px; color: {cor}; font-weight: bold;">{res['score']}</div>
        <hr style="width: 50%; margin: 40px auto;">
        <div style="font-size: 30px;">
            <p>IBOVESPA: {res['ibov']}%</p>
            <p>DÓLAR: {res['dolar']}%</p>
            <p>PETRÓLEO: {res['pet']}%</p>
        </div>
        <script>setTimeout(function(){{ location.reload(); }}, 120000);</script>
    </body>
    """

if _name_ == "_main_":
    app.run(host='0.0.0.0', port=5000)





