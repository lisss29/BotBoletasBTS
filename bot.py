import os
import time
import random
import sys
import requests
from concurrent.futures import ThreadPoolExecutor

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URLS = [
    "https://www.ticketmaster.co/event/bts-world-tour-venta-general-sabado-3-octubre",
    "https://www.ticketmaster.co/event/bts-world-tour-venta-general-viernes-2-octubre"
]

def log(msg):
    print(msg)
    sys.stdout.flush()

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        log(f"Error Telegram: {e}")

# ⚙️ crear driver
def crear_driver():
    options = Options()
    options.binary_location = "/usr/bin/chromium"
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0")

    service = Service("/usr/bin/chromedriver")
    return webdriver.Chrome(service=service, options=options)

log("🚀 Iniciando ULTRA PRO...")

try:
    driver1 = crear_driver()
    driver2 = crear_driver()
    send_telegram("🚀 ULTRA PRO activo")
except Exception as e:
    log(f"❌ Error Chrome: {e}")
    exit()

estado_anterior = {url: None for url in URLS}

# 🔍 detección combinada
def detectar(driver, url):
    try:
        driver.get(url)
        time.sleep(random.randint(3, 6))

        # botón real
        botones = driver.find_elements(By.CSS_SELECTOR, "button")
        for b in botones:
            txt = b.text.lower()
            if any(x in txt for x in ["comprar", "buy", "tickets", "entradas"]):
                return "disponible"

        # fallback texto
        body = driver.page_source.lower()
        if any(x in body for x in ["agotado", "sold out", "no hay entradas"]):
            return "agotado"

        return "desconocido"

    except:
        return "error"

# 🔁 doble verificación en paralelo
def verificar(url):
    with ThreadPoolExecutor(max_workers=2) as executor:
        resultados = list(executor.map(
            lambda d: detectar(d, url),
            [driver1, driver2]
        ))

    # consenso
    if resultados.count("disponible") >= 2:
        return "disponible"
    elif resultados.count("agotado") >= 2:
        return "agotado"
    else:
        return "inestable"

def ciclo():
    for url in URLS:
        estado = verificar(url)

        log(f"📊 {url} → {estado}")

        if estado != estado_anterior[url]:
            if estado == "disponible":
                send_telegram(f"🔥 DISPONIBLE 🔥\n{url}")
            elif estado == "agotado":
                send_telegram(f"❌ AGOTADO\n{url}")
            else:
                send_telegram(f"⚠️ Estado: {estado}\n{url}")

            estado_anterior[url] = estado

while True:
    log("🔁 ULTRA ciclo...")
    ciclo()

    espera = random.randint(35, 60)
    log(f"⏳ Esperando {espera}s\n")
    time.sleep(espera)