import requests
from bs4 import BeautifulSoup
import telegram
import time
from flask import Flask


app = Flask("")

@app.route("/")
def home():
    return "Bot attivo!"

# Avvia Flask in background
import threading
def run():
    app.run(host="0.0.0.0", port=8080)
threading.Thread(target=run).start()

# ⚙️ CONFIGURAZIONE
URL = "https://www.amazon.it/-/en/gp/product/B08H26JMB6"
HEADERS = {"User-Agent": "Mozilla/5.0"}
TOKEN = "8384938252:AAGhhyB9hg3NcgjWOkz1lylaDVao2BPvjEs"
CHAT_ID = 2087698457
INTERVAL = 10 * 60       # Controllo rapido ogni 10 minuti
REPORT_INTERVAL = 60 * 60  # Report non disponibile ogni ora

bot = telegram.Bot(token=TOKEN)
last_report_time = 0

# Hard-coded iniziale dell'ultimo prezzo conosciuto
last_price = "949,99€"

def parse_price(price_str):
    return float(price_str.replace("€", "").replace(",", "."))

def get_price_arrow(current, previous):
    try:
        curr_val = parse_price(current)
        prev_val = parse_price(previous)
        if curr_val > prev_val:
            return "📈"
        elif curr_val < prev_val:
            return "📉"
    except:
        pass
    return ""

def check_amazon():
    global last_report_time, last_price
    try:
        html = requests.get(URL, headers=HEADERS).text
        soup = BeautifulSoup(html, "html.parser")

        # Disponibilità
        availability_elem = soup.select_one("#availability")
        availability_text = availability_elem.get_text(strip=True) if availability_elem else "Non trovato"

        # Prezzo corrente
        price_elem = soup.select_one("#corePrice_feature_div span.a-price-whole")
        price_frac = soup.select_one("#corePrice_feature_div span.a-price-fraction")
        current_price = f"{price_elem.get_text(strip=True)},{price_frac.get_text(strip=True)}€" if price_elem and price_frac else None

        current_time = time.time()

        if "Disponibile" in availability_text or "Available" in availability_text:
            arrow = get_price_arrow(current_price, last_price) if current_price else ""
            message = (
                f"🎉 Prodotto DISPONIBILE!\n"
                f"💰 Prezzo attuale: {current_price} {arrow}\n"
                f"💸 Prezzo precedente: {last_price}\n"
                f"🔗 {URL}"
            )
            if current_price:
                last_price = current_price  # aggiorna ultimo prezzo noto
            bot.send_message(chat_id=CHAT_ID, text=message)
            last_report_time = current_time
        else:
            arrow = get_price_arrow(last_price, last_price)  # freccia basata sull’ultimo prezzo noto
            print(f"Non disponibile: {availability_text} | Prezzo stimato: {last_price}")
            if current_time - last_report_time >= REPORT_INTERVAL:
                bot.send_message(
                    chat_id=CHAT_ID,
                    text=f"⏰ Controllo orario: Prodotto NON disponibile.\n💰 Ultimo prezzo noto: {last_price} {arrow}\n🔗 {URL}"
                )
                last_report_time = current_time

    except Exception as e:
        print("Errore:", e)

if __name__ == "__main__":
    bot.send_message(chat_id=CHAT_ID, text="🤖 Bot attivo! Controllo prodotto...")
    while True:
        check_amazon()
        time.sleep(INTERVAL)
