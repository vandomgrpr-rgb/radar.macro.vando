from flask import Flask
import yfinance as yf
import os

app = Flask(__name__)

def calcular_rastro():
    try:
        # Tickers: Ibovespa, Dólar, S&P 500 Futuro, Petróleo Brent
        tickers = ["^BVSP", "BRL=X", "ES=F", "BZ=F"]
        data = yf.download(tickers, period="1d", interval="5m", progress=False)['Close']
        
        if data.empty:
            return None

        # Preço Atual vs Abertura
        atual = data.iloc[-1]
        abertura = data.iloc[0]
        
        v_ibov = ((atual['^BVSP'] / abertura['^BVSP']) - 1) * 100
        v_dolar = ((atual['BRL=X'] / abertura['BRL=X']) - 1) * 100
        v_sp = ((atual['ES=F'] / abertura['ES=F']) - 1) * 100
        v_pet = ((atual['BZ=F'] / abertura['BZ=F']) - 1) * 100

        # CÁLCULO DO RASTRO (Foco na B3)
        # Se Índice cai e Dólar sobe = Score cai (Azedume)
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
    
    # Define a cor do Score (Verde para alta, Vermelho para baixa)
    cor_score = "green" if res['score'] > 0 else "red"
    
    return f"""
    <body style="background-color: black; color: white; font-family: sans-serif; text-align: center; padding-top: 50px;">
        <h1 style="font-size: 50px; margin-bottom: 10px;">RASTRO DO MERCADO</h1>
        <p style="color: gray; font-size: 20px;">Radar 10 - Vando Muniz</p>
        
        <div style="font-size: 160px; color: {cor_score}; font-weight: bold; margin: 40px 0;">
            {res['score']}
        </div>
        
        <div style="font-size: 35px; border-top: 1px solid #333; padding-top: 30px; display: inline-block; width: 80%;">
            <p>IBOVESPA: <b>{res['ibov']}%</b> | DÓLAR: <b>{res['dolar']}%</b></p>
            <p>PETRÓLEO BRENT: <b>{res['pet']}%</b></p>
        </div>
        
        <p style="color: #555; margin-top: 50px;">Atualização automática a cada 2 minutos</p>
        
        <script>
            setTimeout(function(){{
                location.reload();
            }}, 120000);
        </script>
    </body>
    """

if__name__=="__main__":
    # O Render exige o uso da variável de ambiente PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)








