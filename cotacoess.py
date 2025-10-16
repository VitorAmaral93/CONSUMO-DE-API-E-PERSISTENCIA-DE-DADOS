
import requests
import sqlite3
from datetime import datetime

API_KEY = "145adadd" 
API_URL = f"https://api.hgbrasil.com/finance?format=json-cors&key={API_KEY}"
DB_FILE = "bdcotacoes.db"

def obter_cotacoes():
    resp = requests.get(API_URL, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    results = data.get("results")
    if not results:
        raise ValueError("Resposta sem 'results' — verifique a chave.")
    currencies = results.get("currencies", {})
    usd = currencies.get("USD")
    eur = currencies.get("EUR")
    if usd is None or eur is None:
        raise ValueError("USD ou EUR não encontrados na resposta.")
    dolar_buy = usd.get("buy")
    euro_buy = eur.get("buy")
    return dolar_buy, euro_buy

def criar_tabela_se_nao_existir(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS moedas (
            Data TEXT,
            Dolar REAL,
            Euro REAL
        )
    """)
    conn.commit()

def salvar_no_banco(dolar, euro, conn):
    ts = datetime.now().isoformat(timespec='seconds')
    conn.execute("INSERT INTO moedas (Data, Dolar, Euro) VALUES (?, ?, ?)", (ts, dolar, euro))
    conn.commit()
    return ts

def main():
    try:
        dolar, euro = obter_cotacoes()
    except Exception as e:
        print("Erro ao obter cotações:", e)
        return

    conn = sqlite3.connect(DB_FILE)
    criar_tabela_se_nao_existir(conn)
    ts = salvar_no_banco(dolar, euro, conn)
    print(f"Salvo em {DB_FILE} — {ts}")
    print("Dólar (buy):", dolar)
    print("Euro  (buy):", euro)
    conn.close()

if __name__ == "__main__":
    main()