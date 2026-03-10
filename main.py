import yfinance as yf
import time

# Configuração de Tickers
TICKERS = ["^BVSP", "BRL=X", "ES=F", "BZ=F"]

def calcular_rastro_seguro():
    try:
        # Puxamos dados de 1m, mas o Render só vai rodar essa função 
        # em intervalos maiores para evitar bloqueio.
        data = yf.download(TICKERS, period="1d", interval="1m", progress=False)['Close']
        
        if data.empty or len(data) < 2:
            return "Aguardando sinal..."

        atual = data.iloc[-1]
        abertura = data.iloc[0]
        
        # Variações %
        v_ibov = ((atual['^BVSP'] / abertura['^BVSP']) - 1) * 100
        v_dolar = ((atual['BRL=X'] / abertura['BRL=X']) - 1) * 100
        v_sp500 = ((atual['ES=F'] / abertura['ES=F']) - 1) * 100
        v_petroleo = ((atual['BZ=F'] / abertura['BZ=F']) - 1) * 100

        # SCORE: Foco no Derretimento do Índice e Alta do Dólar
        # Peso maior no IBOV e Dólar conforme você pediu
        score_local = (v_ibov * 0.6) - (v_dolar * 0.4)
        score_global = (v_sp500 * 0.5) - (v_petroleo * 0.5)
        
        score_final = score_local + score_global
        
        return {
            "score": round(score_final, 3),
            "ibov": round(v_ibov, 2),
            "dolar": round(v_dolar, 2),
            "petroleo": round(v_petroleo, 2),
            "sp500": round(v_sp500, 2)
        }
    except Exception as e:
        return f"Erro: {e}"

# DICA: Se você usa um loop no Render, coloque um time.sleep(300) 
# para ele rodar apenas a cada 5 minutos (300 segundos).




