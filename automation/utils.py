import asyncio
from playwright.async_api import async_playwright
import requests
import random
import subprocess
import time
import os
import shutil
import logging

# Number of concurrent browser instances per batch
BATCH_SIZE = 2
# Total runs (each batch opens BATCH_SIZE browsers)
TOTAL_BATCHES = 10

MOBILE_DEVICES = [
    {"device": "iPhone 12", "width": 390, "height": 844},
    {"device": "Pixel 5", "width": 393, "height": 851},
    {"device": "Samsung Galaxy S20", "width": 412, "height": 915},
    {"device": "iPhone SE", "width": 375, "height": 667},
    {"device": "Samsung Galaxy Note 10", "width": 412, "height": 869},
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("browser_automation.log", mode="a", encoding="utf-8")
    ]
)

def get_public_ip():
    try:
        response = requests.get('https://api64.ipify.org?format=json', timeout=5)
        if response.status_code == 200:
            ip = response.json().get('ip')
            logging.info(f"Current IP Address: {ip}")
            return ip
    except requests.RequestException as e:
        logging.error(f"Error getting IP address: {e}")
    return "Unknown"

def clear_chrome_cache():
    try:
        subprocess.run("taskkill /F /IM chrome.exe /T", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)
        chrome_data_path = os.path.expanduser("~") + r"\AppData\Local\Google\Chrome\User Data"
        if os.path.exists(chrome_data_path):
            shutil.rmtree(chrome_data_path, ignore_errors=True)
            logging.info("[+] Chrome Cache Cleared.")
    except Exception as e:
        logging.error(f"Error clearing cache: {e}")

async def goto_with_retry(page, url, retries=3, delay=3):
    attempt = 0
    while attempt < retries:
        try:
            await page.goto(url, wait_until="networkidle")
            return
        except Exception as e:
            logging.error(f"Error navigating to {url}, attempt {attempt + 1}: {e}")
            attempt += 1
            await asyncio.sleep(delay)

def check_vpn():
    vpn_ip = get_public_ip()
    if vpn_ip.startswith("Error") or "India" in vpn_ip:
        logging.error("VPN not working! Still showing real location.")
        return False
    return True

async def open_website(device, url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={"width": device["width"], "height": device["height"]},
            user_agent=f"Mozilla/5.0 (Linux; Android 10; {device['device']}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.93 Mobile Safari/537.36",
            permissions=["geolocation"],
            ignore_https_errors=True
        )
        page = await context.new_page()
        await goto_with_retry(page, url)
        logging.info(f"Browser opened with device: {device['device']}")
        for _ in range(3):
            await page.mouse.wheel(0, 500)
            await asyncio.sleep(random.uniform(1, 2))
        await asyncio.sleep(random.uniform(5, 10))
        await browser.close()

async def run_batches(url):
    if not check_vpn():
        return "VPN Not Working!"
    for batch in range(TOTAL_BATCHES):
        logging.info(f"Running Batch {batch + 1} / {TOTAL_BATCHES}")
        tasks = [open_website(random.choice(MOBILE_DEVICES), url) for _ in range(BATCH_SIZE)]
        await asyncio.gather(*tasks)
        logging.info(f"Batch {batch + 1} completed. Waiting before next batch...")
        await asyncio.sleep(random.uniform(5, 10))
    return "Task Completed"

def run_bot():
    url = "https://furtivelywhipped.com/vdgv3dzm?key=b90255b01cb0e9f0a0f85a7aa857d3bb"
    asyncio.run(run_batches(url))
