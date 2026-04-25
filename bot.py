import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# 🔐 Variables de entorno (NO pongas tokens en el código)
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URLS = [
    "https://www.ticketmaster.co/event/bts-world-tour-venta-general-sabado-3-octubre",
    "https://www.ticketmaster.co/event/bts-world-tour-venta-general-viernes-2-octubre"
]

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        print("Error enviando mensaje:", e)

# ⚙️ Configuración de Chrome para Railway
options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

print("🚀 Bot iniciado en Railway")

# 🔁 Control para no enviar spam
avisado = {url: False for url in URLS}

def check():
    for url in URLS:
        try:
            driver.get(url)
            time.sleep(6)

            body = driver.page_source.lower()

            disponible = not any(x in body for x in [
                "agotado",
                "sold out",
                "no hay entradas"
            ])

            if disponible:
                if not avisado[url]:
                    send_telegram(f"🔥 BOLETAS DISPONIBLES:\n{url}")
                    print("🔥 DISPONIBLE:", url)
                    avisado[url] = True
            else:
                print("❌ Aún agotado:", url)
                avisado[url] = False

        except Exception as e:
            print("⚠️ Error revisando:", url)
            print(e)

# 🔁 Loop infinito
while True:
    check()
    print("⏳ Esperando 90 segundos...\n")
    time.sleep(90)