from playwright.async_api import async_playwright
import time
import os
import random
import logging
import requests
from urllib.parse import urlparse
import string
import asyncio

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROXY_FILE = os.path.join(BASE_DIR, r"D:\browserbot\proxy.txt")

# Viewports, Devices, and Browser Versions unchanged
REALISTIC_VIEWPORTS = [
    {"width": 360, "height": 640},   # Samsung Galaxy S22
    {"width": 375, "height": 812},   # iPhone X
    {"width": 390, "height": 844},   # iPhone 13 Mini
    {"width": 414, "height": 896},   # iPhone 11 Pro Max
    {"width": 1920, "height": 1080}, # Full HD
    {"width": 1280, "height": 720},  # HD
]

DEVICES = [
    "iPhone; CPU iPhone OS 16_0 like Mac OS X",  # iPhone 14
    "Linux; Android 13; SM-S918B Build/TP1A.220624.014",  # Galaxy S23 Ultra
    "Windows NT 10.0; Win64; x64 AppleWebKit/537.36",  # Windows Chrome
]


BROWSER_VERSIONS = {
    "Chrome": (90, 120),
    "Firefox": (80, 110),
    "Edge": (90, 120),
}

# Utility functions remain unchanged
def load_proxies():
    try:
        with open(PROXY_FILE, "r", encoding="utf-8") as f:
            proxies = [line.strip() for line in f if line.strip()]
        return proxies
    except Exception as e:
        logging.error(f"Error loading proxies: {e}")
        return []

def is_proxy_working(proxy):
    try:
        parsed_proxy = urlparse(f"http://{proxy}")
        proxy_dict = {
            "http": f"http://{parsed_proxy.netloc}",
            "https": f"https://{parsed_proxy.netloc}",
        }
        response = requests.get("https://api64.ipify.org?format=json", proxies=proxy_dict, timeout=10)
        if response.status_code == 200:
            ip = response.json().get("ip")
            logging.info(f"Proxy working: {proxy} | IP: {ip}")
            return True
    except Exception as e:
        logging.warning(f"Proxy failed: {proxy} | Error: {e}")
    return False

failed_proxies = set()

async def get_valid_proxy():
    proxies = load_proxies()
    random.shuffle(proxies)
    for proxy in proxies:
        if proxy in failed_proxies:
            continue
        if is_proxy_working(proxy):
            return proxy
        failed_proxies.add(proxy)
    return None

def generate_dynamic_cookies():
    def random_string(length=10):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    uncs_values = str(random.randint(1, 10))
    return {
        "pdhtkv": "true",
        "pdhtkv28": "true",
        "u_pl25543386": "1",
        'u_pl26376953': '1',
        "iprc" + random_string(32): str(random.randint(1000000, 9999999)),
        'uncs': uncs_values,
        'uncs28': uncs_values,
        'cjs': 't',
    }
    

def get_random_user_agent(proxy_geo=None):
    device = random.choice(DEVICES)
    browser = random.choice(list(BROWSER_VERSIONS.keys()))
    version_range = BROWSER_VERSIONS[browser]
    version = random.randint(*version_range)
    language = proxy_geo.get("language", "en-US") if proxy_geo else "en-US"
    platform = "Win32" if "Windows" in device else "Macintosh"

    if "iPhone" in device or "iPad" in device:
        return f"Mozilla/5.0 ({device}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{version}.0 Mobile Safari/604.1"
    elif "Android" in device:
        return f"Mozilla/5.0 ({device}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Mobile Safari/537.36"
    elif "Windows" in device:
        return f"Mozilla/5.0 ({device}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36"
    elif "Macintosh" in device:
        return f"Mozilla/5.0 ({device}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36"
    else:
        return f"Mozilla/5.0 ({device}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36"

def get_ip_geo(proxy=None):
    try:
        if proxy:
            creds, host_port = proxy.split("@")
            username, password = creds.split(":")
            proxy_url = f"http://{username}:{password}@{host_port}"
            response = requests.get("https://ipinfo.io/json", proxies={"http": proxy_url, "https": proxy_url}, timeout=10)
            data = response.json()
            lat, lon = map(float, data["loc"].split(","))
            return {
                "latitude": lat,
                "longitude": lon,
                "timezone": data.get("timezone", "UTC"),
                "language": data.get("country", "US").lower() + "-en",
            }
    except Exception as e:
        logging.warning(f"Geo fallback used: {e}")
    return {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "timezone": "America/Los_Angeles",
        "language": "en-US",
    }

# Fingerprint spoofing enhancements
async def spoof_fingerprints(context, geo):
    logging.info("Spoofing browser fingerprints...")
    await context.add_init_script(
        f"""
        Object.defineProperty(navigator, 'languages', {{
            get: () => ['{geo['language']}', 'en']
        }});
        Intl.DateTimeFormat.prototype.resolvedOptions = function () {{
            return {{ timeZone: '{geo['timezone']}' }};
        }};
        Object.defineProperty(navigator, 'doNotTrack', {{ get: () => '1' }});
        Object.defineProperty(navigator, 'platform', {{ get: () => 'Win32' }});
        Object.defineProperty(navigator, 'deviceMemory', {{ get: () => 16 }});
        Object.defineProperty(navigator, 'hardwareConcurrency', {{ get: () => 12 }});
        navigator.geolocation.getCurrentPosition = function(success) {{
            success({{
                coords: {{
                    latitude: {geo['latitude']},
                    longitude: {geo['longitude']},
                    accuracy: 100
                }}
            }});
        }};
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(p) {{
            if (p === 37445) return "Google Inc. (NVIDIA)";
            if (p === 37446) return "NVIDIA GeForce RTX 2080 Super with Max-Q Design";
            return getParameter.call(this, p);
        }};
        const toBlob = HTMLCanvasElement.prototype.toBlob;
        HTMLCanvasElement.prototype.toBlob = function() {{
            const ctx = this.getContext('2d');
            ctx.fillStyle = 'rgb(100,100,100)';
            ctx.fillRect(0, 0, this.width, this.height);
            return toBlob.apply(this, arguments);
        }};
        const oscillatorStart = OscillatorNode.prototype.start;
        OscillatorNode.prototype.start = function() {{
            this.frequency.value = 440 + Math.random() * 0.01;
            return oscillatorStart.apply(this, arguments);
        }};
        window.speechSynthesis.getVoices = function() {{
            return [{{
                voiceURI: 'Google US English',
                name: 'Google US English',
                lang: '{geo['language']}',
                localService: true,
                default: true
            }}];
        }};
        Object.defineProperty(navigator, 'webdriver', {{ get: () => undefined }});
    """
    )
    logging.info("Browser fingerprints spoofed successfully.")




async def main():
    while True:
        try:
            valid_proxy = await get_valid_proxy()
            if not valid_proxy:
                logging.error("No valid proxies found.")
                break

            parsed_proxy = urlparse(f"http://{valid_proxy}")
            username_password, host_port = parsed_proxy.netloc.split("@", 1)
            username, password = username_password.split(":", 1)
            host, port = host_port.split(":", 1)

            proxy_config = {
                "server": f"{host}:{port}",
                "username": username,
                "password": password,
            }

            viewport = random.choice(REALISTIC_VIEWPORTS)
            is_mobile = viewport["width"] < 600
            dpr = 3 if is_mobile else 1
            geo_data = get_ip_geo(valid_proxy)
            user_agent = get_random_user_agent(geo_data)
            
            
            async with async_playwright() as p:
                # Launch browser (headless=False to see what's happening)
                browser =await p.chromium.launch(
                    headless=False,
                    proxy=proxy_config,
                    args=["--disable-blink-features=AutomationControlled"],
                )
                context = await browser.new_context(
                    user_agent=user_agent,
                    viewport=viewport,
                    device_scale_factor=dpr,
                    is_mobile=is_mobile,
                    ignore_https_errors=True,
                )
                
                dynamic_cookies = generate_dynamic_cookies()
                await context.add_cookies([
                    {"name": name, "value": value, "domain": "www.profitableratecpm.com", "path": "/"}
                    for name, value in dynamic_cookies.items()
                ])
                
                await spoof_fingerprints(context, geo_data)


                page =await context.new_page()

                # Go to the target site
                await page.goto("https://news-hub-indol.vercel.app/")
                await page.wait_for_load_state("networkidle")  # Wait until page finishes loading

                # Query all matching image elements
                selector = "div.relative.h-48.w-full"
                images = await page.query_selector_all(selector)

                print(f"Found {len(images)} matching images.")

                for i, img in enumerate(images):
                    print(f"Clicking image #{i + 1} (Ctrl + click)...")
                    # Perform Ctrl + click
                    await img.click(modifiers=[ "Control" ])

                    print(f"Image #{i + 1} clicked.")
                    time.sleep(10)  # Wait 10 seconds before next click

                # Optional: keep browser open a bit longer to view results
                time.sleep(5)

                await context.clear_cookies()
                await page.evaluate("""
                    try {
                        window.localStorage.clear();
                        window.sessionStorage.clear();
                    } catch (error) {
                        console.warn('Failed to clear localStorage/sessionStorage:', error.message);
                    }
                """)
                
                # Cleanup
                context.close()
                browser.close()
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            continue

if __name__ == "__main__":
    asyncio.run(main())