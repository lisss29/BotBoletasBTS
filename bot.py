import os
import time
import requests
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# 🔐 Variables de entorno
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URLS = [
    "https://www.ticketmaster.co/event/bts-world-tour-venta-general-sabado-3-octubre",
    "https://www.ticketmaster.co/event/bts-world-tour-venta-general-viernes-2-octubre"
]

# 🧠 Función de logs (para Railway)
def log(msg):
    print(msg)
    sys.stdout.flush()

# 📲 Telegram
def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        log(f"Error Telegram: {e}")

log("🚀 Iniciando bot...")

# ⚙️ Configuración Chrome (Railway)
options = Options()
options.binary_location = "/usr/bin/chromium"
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service("/usr/bin/chromedriver")

try:
    driver = webdriver.Chrome(service=service, options=options)
    log("✅ Chrome iniciado correctamente")
    send_telegram("🚀 Bot iniciado correctamente en Railway")
except Exception as e:
    log(f"❌ Error iniciando Chrome: {e}")
    exit()

# 🔁 Control anti-spam
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
                    log(f"🔥 DISPONIBLE: {url}")
                    avisado[url] = True
            else:
                log(f"❌ Aún agotado: {url}")
                avisado[url] = False

        except Exception as e:
            log(f"⚠️ Error revisando {url}: {e}")

# 🔁 Loop infinito
while True:
    log("🔁 Ejecutando check...")
    check()
    log("⏳ Esperando 90 segundos...\n")
    time.sleep(90)