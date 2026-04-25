import os
import time
import random
import sys
import requests
import smtplib
from email.mime.text import MIMEText
from concurrent.futures import ThreadPoolExecutor

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# =========================
# 🔐 VARIABLES DE ENTORNO
# =========================
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

EMAIL = os.getenv("EMAIL")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH")
TWILIO_FROM = os.getenv("TWILIO_FROM")  # "whatsapp:+14155238886"
TWILIO_TO = os.getenv("TWILIO_TO")      # "whatsapp:+57XXXXXXXXXX"

URLS = [
    "https://www.ticketmaster.co/event/bts-world-tour-venta-general-sabado-3-octubre",
    "https://www.ticketmaster.co/event/bts-world-tour-venta-general-viernes-2-octubre"
]

# =========================
# 🧠 LOG (Railway)
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

# =========================
# 📧 EMAIL (GMAIL)
# =========================
def send_email(msg):
    if not (EMAIL and EMAIL_PASS and EMAIL_TO):
        return
    try:
        mensaje = MIMEText(msg)
        mensaje["Subject"] = "Alerta Boletas"
        mensaje["From"] = EMAIL
        mensaje["To"] = EMAIL_TO

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, EMAIL_PASS)
        server.send_message(mensaje)
        server.quit()
    except Exception as e:
        log(f"Error Email: {e}")

# =========================
# 💬 WHATSAPP (TWILIO)
# =========================
def send_whatsapp(msg):
    if not (TWILIO_SID and TWILIO_AUTH and TWILIO_FROM and TWILIO_TO):
        return
    try:
        from requests.auth import HTTPBasicAuth
        requests.post(
            f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json",
            data={"From": TWILIO_FROM, "To": TWILIO_TO, "Body": msg},
            auth=HTTPBasicAuth(TWILIO_SID, TWILIO_AUTH)
        )
    except Exception as e:
        log(f"Error WhatsApp: {e}")

# =========================
# 🚨 ALERTA EXTREMA
# =========================
def alerta_extrema(msg):
    # Telegram en ráfaga
    for _ in range(5):
        send_telegram(f"🚨 ALERTA 🚨\n{msg}")
        time.sleep(1.2)

    # Email (1 envío)
    send_email(f"🚨 ALERTA BOLETAS 🚨\n{msg}")

    # WhatsApp (1 envío)
    send_whatsapp(f"🚨 DISPONIBLE 🚨\n{msg}")

# =========================
# ⚙️ SELENIUM (2 drivers)
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

def wait_dom(driver, timeout=8):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(("css selector", "body"))
        )
    except:
        pass

log("🚀 Iniciando BOT ULTRA PRO...")

try:
    driver1 = crear_driver()
    driver2 = crear_driver()
    send_telegram("🚀 Bot ULTRA PRO activo")
except Exception as e:
    log(f"❌ Error iniciando Chrome: {e}")
    exit()

# =========================
# 🧠 ESTADO
# =========================
estado_anterior = {url: None for url in URLS}

# =========================
# 🔍 DETECCIÓN
# =========================
def detectar(driver, url):
    try:
        driver.get(url)
        wait_dom(driver, 8)
        time.sleep(random.uniform(1.5, 3.0))

        # 1) Botón real
        botones = driver.find_elements(By.CSS_SELECTOR, "button")
        for b in botones:
            txt = b.text.lower()
            if any(x in txt for x in ["comprar", "buy", "tickets", "entradas"]):
                return "disponible"

        # 2) Fallback texto
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

    if resultados.count("disponible") >= 2:
        return "disponible"
    elif resultados.count("agotado") >= 2:
        return "agotado"
    else:
        return "inestable"

# =========================
# 🔁 CICLO
# =========================
def ciclo():
    for url in URLS:
        estado = verificar(url)
        log(f"📊 {url} → {estado}")

        if estado != estado_anterior[url]:
            if estado == "disponible":
                alerta_extrema(url)  # 🔥 ALERTA MÁXIMA
            elif estado == "agotado":
                send_telegram(f"❌ AGOTADO\n{url}")
                send_email(f"❌ AGOTADO\n{url}")
            else:
                send_telegram(f"⚠️ Estado: {estado}\n{url}")

            estado_anterior[url] = estado

# =========================
# 🔁 LOOP PRINCIPAL
# =========================
while True:
    log("🔁 Ciclo ULTRA PRO...")
    ciclo()

    espera = random.randint(25, 45)
    log(f"⏳ Esperando {espera}s\n")
    time.sleep(espera)