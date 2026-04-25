import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

URLS = [
    "https://www.ticketmaster.co/event/bts-world-tour-venta-general-sabado-3-octubre",
    "https://www.ticketmaster.co/event/bts-world-tour-venta-general-viernes-2-octubre"
]

TOKEN = "8060171083:AAG_EbWvr3_D1wa-e4Tr_LhB0QO_Hrf-Gus"
CHAT_ID = "2032428099"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{8060171083:AAG_EbWvr3_D1wa-e4Tr_LhB0QO_Hrf-Gus}/sendMessage"
    requests.post(url, data={"2032428099": CHAT_ID, "text": msg})

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

def check():
    for url in URLS:
        driver.get(url)
        time.sleep(6)

        body = driver.page_source.lower()

        if not any(x in body for x in ["agotado", "sold out", "no hay entradas"]):
            send_telegram(f"🔥 BOLETAS DISPONIBLES:\n{url}")
            print("DISPONIBLE", url)
        else:
            print("agotado", url)

while True:
    check()
    time.sleep(90)