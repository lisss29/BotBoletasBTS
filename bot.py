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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# =========================
# 🔐 ENV
# =========================
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URLS = [
    "https://www.ticketmaster.co/event/bts-world-tour-venta-general-sabado-3-octubre",
    "https://www.ticketmaster.co/event/bts-world-tour-venta-general-viernes-2-octubre"
]

# =========================
# 🧠 LOG
# =========================
def log(msg):
    print(msg)
    sys.stdout.flush()

# =========================
# 📲 TELEGRAM
# =========================
def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        log(f"Error Telegram: {e}")

def alerta_extrema(msg):
    # ráfaga para no perderla
    for _ in range(5):
        send_telegram(f"🚨 ALERTA 🚨\n{msg}")
        time.sleep(1.1)

# =========================
# ⚙️ SELENIUM
# =========================
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

def wait_dom(driver, timeout=6):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(("css selector", "body"))
        )
    except:
        pass

log("🚀 Iniciando BOT (refresh inteligente + prioridad)...")

try:
    driver1 = crear_driver()
    driver2 = crear_driver()

    # 🔥 “calentar” sesión/cookies (reduce latencia posterior)
    driver1.get("https://www.ticketmaster.co")
    driver2.get("https://www.ticketmaster.co")
    time.sleep(4)

    # 🔥 primera carga de eventos
    for d in (driver1, driver2):
        for url in URLS:
            d.get(url)
            wait_dom(d, 6)

    send_telegram("🚀 Bot activo y monitoreando")
except Exception as e:
    log(f"❌ Error iniciando Chrome: {e}")
    exit()

# =========================
# 🧠 ESTADO
# =========================
estado_anterior = {url: None for url in URLS}
primera_vez = {url: True for url in URLS}

# =========================
# 🔍 DETECCIÓN (prioritaria)
# =========================
def detectar(driver, url):
    try:
        # ⚡ refresh inteligente
        if primera_vez[url]:
            driver.get(url)
            primera_vez[url] = False
        else:
            driver.refresh()

        wait_dom(driver, 6)
        time.sleep(random.uniform(0.8, 1.6))  # micro-pausa humana

        # ⚡ selector directo (más rápido)
        elementos = driver.find_elements(By.CSS_SELECTOR, "[data-testid*='purchase'], button")

        # 🧠 PRIORIDAD: si vemos botón de compra, salimos YA
        for el in elementos:
            txt = el.text.lower()
            if any(x in txt for x in ["comprar", "buy", "tickets", "entradas"]):
                return "disponible"

        # fallback texto
        body = driver.page_source.lower()
        if any(x in body for x in ["agotado", "sold out", "no hay entradas"]):
            return "agotado"

        return "desconocido"

    except Exception as e:
        log(f"⚠️ Error detectar: {e}")
        return "error"

# =========================
# 🔁 VERIFICACIÓN PARALELA
# =========================
def verificar(url):
    with ThreadPoolExecutor(max_workers=2) as executor:
        resultados = list(executor.map(lambda d: detectar(d, url), [driver1, driver2]))

    # ⚡ PRIORIDAD: si uno ve disponible → avisar de una
    if "disponible" in resultados:
        return "disponible"

    # consenso para agotado
    if resultados.count("agotado") >= 2:
        return "agotado"

    return "inestable"

# =========================
# 🔁 CICLO
# =========================
def ciclo():
    for url in URLS:
        estado = verificar(url)
        log(f"📊 {url} → {estado}")

        # 🔔 aviso solo si cambia (menos spam)
        if estado != estado_anterior[url]:
            if estado == "disponible":
                alerta_extrema(f"🔥 DISPONIBLE 🔥\n{url}")
            elif estado == "agotado":
                send_telegram(f"❌ AGOTADO\n{url}")
            else:
                send_telegram(f"⚠️ Estado: {estado}\n{url}")

            estado_anterior[url] = estado

# =========================
# 🔁 LOOP
# =========================
while True:
    log("🔁 Ciclo activo...")
    ciclo()

    # ⚡ más rápido pero con variación humana
    espera = random.randint(20, 35)
    log(f"⏳ Esperando {espera}s\n")
    time.sleep(espera)