import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

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
        print("Error Telegram:", e)

print("🚀 Iniciando bot...")

# ⚙️ CONFIGURACIÓN CORRECTA PARA RAILWAY
options = Options()
options.binary_location = "/usr/bin/chromium"
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service("/usr/bin/chromedriver")

try:
    driver = webdriver.Chrome(service=service, options=options)
    print("✅ Chrome iniciado correctamente")
    send_telegram("🚀 Bot iniciado correctamente en Railway")
except Exception as e:
    print("❌ Error iniciando Chrome:", e)
    exit()

avisado = {url: False for url in URLS}

def check():
    for url in URLS:
        try:
            driver.get(url)
            time.sleep(6)

            body = driver.page_source.lower()

            disponible = not any(x in body for x in [
                "agotado", "sold out", "no hay entradas"
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
            print("⚠️ Error revisando:", url, e)

while True:
    check()
    print("⏳ Esperando 90 segundos...\n")
    time.sleep(90)