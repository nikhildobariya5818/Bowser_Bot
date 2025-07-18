import asyncio
from playwright.async_api import async_playwright
import random
import requests
import logging
import os
from urllib.parse import urlparse
import string

# Configure loggingA
logging.basicConfig(level=logging.INFO)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROXY_FILE = os.path.join(BASE_DIR, r"D:\browserbot\proxy.txt")

REALISTIC_VIEWPORTS = [
    # Mobile portrait
    {"width": 360, "height": 640},   # Samsung Galaxy S22
    {"width": 375, "height": 812},   # iPhone X
    {"width": 390, "height": 844},   # iPhone 13 Mini
    {"width": 414, "height": 896},   # iPhone 11 Pro Max

    # Mobile landscape
    {"width": 640, "height": 360},   # Landscape - Samsung Galaxy S22
    {"width": 812, "height": 375},   # Landscape - iPhone X
    {"width": 896, "height": 414},   # Landscape - iPhone 11 Pro Max

    # Tablets
    {"width": 768, "height": 1024},  # iPad Portrait
    {"width": 1024, "height": 768},  # iPad Landscape
    {"width": 820, "height": 1180},  # iPad Air Portrait
    {"width": 1180, "height": 820},  # iPad Air Landscape

    # Desktops
    {"width": 1280, "height": 720},  # HD
    {"width": 1920, "height": 1080}, # Full HD
    {"width": 1440, "height": 900},  # Widescreen
]

DEVICES = [
        # iPhone 14 Series
        "iPhone; CPU iPhone OS 16_0 like Mac OS X",  # iPhone 14
        "iPhone; CPU iPhone OS 16_0 like Mac OS X",  # iPhone 14 Plus
        "iPhone; CPU iPhone OS 16_0 like Mac OS X",  # iPhone 14 Pro
        "iPhone; CPU iPhone OS 16_0 like Mac OS X",  # iPhone 14 Pro Max
        # iPhone 13 Series
        "iPhone; CPU iPhone OS 15_0 like Mac OS X",  # iPhone 13
        "iPhone; CPU iPhone OS 15_0 like Mac OS X",  # iPhone 13 Mini
        "iPhone; CPU iPhone OS 15_0 like Mac OS X",  # iPhone 13 Pro
        "iPhone; CPU iPhone OS 15_0 like Mac OS X",  # iPhone 13 Pro Max
        # iPhone SE (3rd Gen)
        "iPhone; CPU iPhone OS 15_4 like Mac OS X",  # iPhone SE (2022)
        # iPad Series
        "iPad; CPU OS 17_0 like Mac OS X",  # iPad Air 5 (M1)
        "iPad; CPU OS 17_0 like Mac OS X",  # iPad Mini 6
        # Galaxy S23 Series
        "Linux; Android 13; SM-S918B Build/TP1A.220624.014",  # Galaxy S23 Ultra
        "Linux; Android 13; SM-S916B Build/TP1A.220624.014",  # Galaxy S23+
        "Linux; Android 13; SM-S911B Build/TP1A.220624.014",  # Galaxy S23
        # Galaxy S22 Series
        "Linux; Android 12; SM-S908B Build/SP1A.210812.016",  # Galaxy S22 Ultra
        "Linux; Android 12; SM-S906B Build/SP1A.210812.016",  # Galaxy S22+
        "Linux; Android 12; SM-S901B Build/SP1A.210812.016",  # Galaxy S22
        # Galaxy Z Fold/Flip Series
        "Linux; Android 13; SM-F936B Build/TP1A.220624.014",  # Galaxy Z Fold 4
        "Linux; Android 13; SM-F721B Build/TP1A.220624.014",  # Galaxy Z Flip 4
        # Galaxy A Series
        "Linux; Android 13; SM-A546B Build/TP1A.220624.014",  # Galaxy A54
        "Linux; Android 13; SM-A346B Build/TP1A.220624.014",  # Galaxy A34
        # Pixel 7 Series
        "Linux; Android 13; Pixel 7 Pro Build/TQ1A.230205.002",
        "Linux; Android 13; Pixel 7 Build/TQ1A.230205.002",
        # Pixel 6 Series
        "Linux; Android 12; Pixel 6 Pro Build/SD1A.210817.023",
        "Linux; Android 12; Pixel 6 Build/SD1A.210817.023",
        # Pixel 5
        "Linux; Android 11; Pixel 5 Build/RD1A.201105.003",
        # OnePlus 11 Series
        "Linux; Android 13; CPH2449 Build/OnePlus11Pro",
        "Linux; Android 13; CPH2447 Build/OnePlus11R",
        # OnePlus 10 Series
        "Linux; Android 12; CPH2349 Build/OnePlus10Pro",
        "Linux; Android 12; CPH2347 Build/OnePlus10R",
        # OnePlus Nord Series
        "Linux; Android 13; CPH2429 Build/OnePlusNord3",
        "Linux; Android 12; CPH2229 Build/OnePlusNord2",
        # Xiaomi 14 Series
        "Linux; Android 14; 23111PCD8G Build/Xiaomi14Ultra",
        "Linux; Android 14; 23111PCD8G Build/Xiaomi14Pro",
        # Redmi K Series
        "Linux; Android 14; 23127PN0CC Build/RedmiK70Pro",
        "Linux; Android 14; 23127PN0CC Build/RedmiK70",
        # Poco F Series
        "Linux; Android 14; 23049PCD8G Build/PocoF5Pro",
        "Linux; Android 14; 23049PCD8G Build/PocoF5",
        # Find X Series
        "Linux; Android 14; CPH2495 Build/OPPOFindX7Ultra",
        "Linux; Android 14; CPH2481 Build/OPPOFindX7Pro",
        # Reno Series
        "Linux; Android 14; CPH2481 Build/OPPOReno11Pro",
        "Linux; Android 14; CPH2481 Build/OPPOReno11",
        # X Series
        "Linux; Android 14; V2324A Build/VivoX100Pro",
        "Linux; Android 14; V2324A Build/VivoX100",
        # V Series
        "Linux; Android 14; V2241A Build/VivoV29Pro",
        "Linux; Android 14; V2241A Build/VivoV29",
        # Magic Series
        "Linux; Android 14; ALI-NX1 Build/HonorMagic6Pro",
        "Linux; Android 14; ALI-AN00 Build/HonorMagicV2",
        # X Series
        "Linux; Android 14; ALI-AN00 Build/HonorX10Max",
        "Linux; Android 14; A065 Build/NothingPhone2",
        "Linux; Android 13; A065 Build/NothingPhone1",
        # Windows 11 (Latest Builds)
        "Windows NT 10.0; Win64; x64",  # Generic Windows 11
        "Windows NT 10.0; Win64; x64; rv:109.0",  # Windows 11 with Firefox
        "Windows NT 10.0; Win64; x64 AppleWebKit/537.36",  # Windows 11 with Chrome
        "Windows NT 10.0; WOW64",  # Windows 11 (32-bit emulation on 64-bit)
        "Windows NT 10.0; ARM64",  # Windows 11 on ARM (e.g., Surface Pro X)
        # Windows 10 (Still Widely Used)
        "Windows NT 10.0; Win64; x64",  # Generic Windows 10
        "Windows NT 10.0; WOW64",  # Windows 10 (32-bit emulation on 64-bit)
        "Windows NT 10.0; ARM64",  # Windows 10 on ARM
        # macOS Ventura (13.x)
        "Macintosh; Intel Mac OS X 13_4",  # macOS Ventura on Intel
        "Macintosh; Apple Silicon Mac OS X 13_4",  # macOS Ventura on Apple Silicon (M1/M2)
        # macOS Monterey (12.x)
        "Macintosh; Intel Mac OS X 12_6",  # macOS Monterey on Intel
        "Macintosh; Apple Silicon Mac OS X 12_6",  # macOS Monterey on Apple Silicon
        # macOS Big Sur (11.x)
        "Macintosh; Intel Mac OS X 11_7",  # macOS Big Sur on Intel
        "Macintosh; Apple Silicon Mac OS X 11_7",  # macOS Big Sur on Apple Silicon
       
    ]


BROWSER_VERSIONS = {
    "Chrome": (90, 120),
    "Firefox": (80, 110),
    "Edge": (90, 120),
}


def load_proxies():
    """Load proxies from the file."""
    try:
        logging.info("Loading proxies from file...")
        with open(PROXY_FILE, "r", encoding="utf-8") as f:
            proxies = [line.strip() for line in f if line.strip()]
        logging.info(f"Loaded {len(proxies)} proxies successfully.")
        return proxies
    except Exception as e:
        logging.error(f"Error loading proxies: {e}")
        return []


def is_proxy_working(proxy):
    parsed_proxy = urlparse(f"http://{proxy}")
    proxy_dict = {
        "http": f"http://{parsed_proxy.netloc}",
        "https": f"https://{parsed_proxy.netloc}",
    }
    try:
        logging.info(f"Testing proxy: {proxy}")
        response = requests.get(
            "https://api64.ipify.org?format=json",
            proxies=proxy_dict,
            timeout=10,
            verify=False,
        )
        if response.status_code == 200:
            ip = response.json().get("ip")
            logging.info(f"Proxy working: {proxy} | IP: {ip}")
            return True
    except requests.exceptions.RequestException as e:
        logging.warning(f"Proxy failed: {proxy} | Error: {e}")
    return False
failed_proxies = set()

async def get_valid_proxy():
    proxies = load_proxies()
    random.shuffle(proxies)
    for proxy in proxies:
        if proxy in failed_proxies:
            continue  # Skip previously failed proxies
        if is_proxy_working(proxy):
            logging.info(f"Found valid proxy: {proxy}")
            return proxy
        failed_proxies.add(proxy)  # Mark as failed
    logging.error("No valid proxies found.")
    return None


def generate_dynamic_cookies():
    """Generate dynamic cookies."""
    def random_string(length=10):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    uncs_values = str(random.randint(1, 10))
    # Generate unique cookie values, ensuring all values are strings
    cookies = {
        "pdhtkv": "true",
        "pdhtkv28": "true",
        "u_pl25543386": "1",
        'u_pl26376953': '1',
        "iprc" + random_string(32): str(random.randint(1000000, 9999999)),  # Convert to string
        'uncs': uncs_values,  # Convert to string
        'uncs28': uncs_values,  # Convert to string
        'cjs': 't',
    }
    logging.info(f"Generated dynamic cookies: {cookies}")
    return cookies


def get_random_user_agent(proxy_geo=None):
    device = random.choice(DEVICES)
    browser = random.choice(list(BROWSER_VERSIONS.keys()))
    version_range = BROWSER_VERSIONS[browser]
    version = random.randint(*version_range)

    if proxy_geo:
        language = proxy_geo.get("language", "en-US")
        platform = "Win32" if "Windows" in device else "Macintosh"
    else:
        language = "en-US"
        platform = "Win32"

    # iOS Devices
    if "iPhone" in device or "iPad" in device:
        user_agent = (
            f"Mozilla/5.0 ({device}) AppleWebKit/605.1.15 (KHTML, like Gecko) "
            f"Version/{version}.0 Mobile/15E148 Safari/604.1"
        )
    # Android Devices
    elif "Android" in device:
        user_agent = (
            f"Mozilla/5.0 ({device}) AppleWebKit/537.36 (KHTML, like Gecko) "
            f"Chrome/{version}.0.0.0 Mobile Safari/537.36"
        )
    # macOS Devices
    elif "Macintosh" in device:
        user_agent = (
            f"Mozilla/5.0 ({device}) AppleWebKit/537.36 (KHTML, like Gecko) "
            f"Chrome/{version}.0.0.0 Safari/537.36"
        )
    # Windows Devices
    elif "Windows" in device:
        if browser == "Firefox":
            user_agent = (
                f"Mozilla/5.0 ({device}; rv:{version}.0) Gecko/20100101 Firefox/{version}.0"
            )
        else:  # Chrome or Edge
            user_agent = (
                f"Mozilla/5.0 ({device}) AppleWebKit/537.36 (KHTML, like Gecko) "
                f"{browser}/{version}.0.0.0 Safari/537.36"
            )
    else:
        # Fallback
        user_agent = (
            f"Mozilla/5.0 ({device}) AppleWebKit/537.36 (KHTML, like Gecko) "
            f"{browser}/{version}.0.0.0 Safari/537.36"
        )

    logging.info(f"Generated random User-Agent: {user_agent}")
    return user_agent

def get_ip_geo(proxy=None):
    try:
        logging.info("Fetching IP geo data...")
        if proxy:
            creds, host_port = proxy.split("@")
            username, password = creds.split(":")
            proxy_url = f"http://{username}:{password}@{host_port}"
            proxy_dict = {
                "http": proxy_url,
                "https": proxy_url,
            }
            response = requests.get(
                "https://ipinfo.io/json",
                proxies=proxy_dict,
                timeout=10,
                verify=False,
            )
            response.raise_for_status()
            data = response.json()
            lat, lon = map(float, data["loc"].split(","))
            geo_data = {
                "latitude": lat,
                "longitude": lon,
                "timezone": data.get("timezone", "UTC"),
                "language": data.get("country", "US").lower() + "-en",
            }
            logging.info(f"IP geo data retrieved: {geo_data}")
            return geo_data
    except Exception as e:
        logging.error(f"Failed to fetch IP geo data: {e}")
        fallback_geo = {
            "latitude": 37.7749,
            "longitude": -122.4194,
            "timezone": "America/Los_Angeles",
            "language": "en-US",
        }
        logging.warning(f"Using fallback geo data: {fallback_geo}")
        return fallback_geo


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

async def update_cookies(context, domain):
    """Update cookies dynamically for the given domain."""
    logging.info("Generating new dynamic cookies...")
    dynamic_cookies = generate_dynamic_cookies()
    
    # Clear existing cookies for the domain (optional)
    await context.clear_cookies()
    
    # Add new cookies to the context
    await context.add_cookies([
        {"name": name, "value": value, "domain": domain, "path": "/"}
        for name, value in dynamic_cookies.items()
    ])
    logging.info(f"Updated dynamic cookies for domain: {domain}")

async def mimic_human_behavior(page, context):
    """Simulate human-like behavior with dynamic cookie updates."""
    try:
        # Simulate random mouse movements
        await page.mouse.move(random.randint(0, 500), random.randint(0, 500))
        await asyncio.sleep(random.uniform(0.5, 2))  # Random delay
        
        # Update cookies before interacting
        await update_cookies(context, "www.profitableratecpm.com")
        
        # Simulate scrolling
        await page.evaluate("window.scrollBy(0, window.innerHeight);")
        await asyncio.sleep(random.uniform(1, 3))  # Random delay
        
        # Update cookies again before clicking
        await update_cookies(context, "www.profitableratecpm.com")
        
        # Simulate clicking on a button or element
        await page.click("button.some-button-selector")  # Replace with actual selector
        await asyncio.sleep(random.uniform(1, 2))  # Random delay
        
    except Exception as e:
        logging.error(f"Error during mimic_human_behavior: {e}")
        

async def main():
    """Main function to automate browser actions with proxy."""
    while True:  # Infinite loop to keep opening browsers one by one
        try:
            valid_proxy = await get_valid_proxy()
            if not valid_proxy:
                logging.error("Exiting due to lack of valid proxies.")
                break  # Exit the loop if no valid proxies are found
            
            # Parse proxy into components
            parsed_proxy = urlparse(f"http://{valid_proxy}")
            username_password, host_port = parsed_proxy.netloc.split("@", 1)
            username, password = username_password.split(":", 1)
            host, port = host_port.split(":", 1)
            proxy_config = {
                "server": f"http://{host}:{port}",
                "username": username,
                "password": password,
            }
            
            async with async_playwright() as p:
                # Launch browser with proxy
                logging.info(f"Launching browser with proxy: {valid_proxy}")
                viewport = random.choice(REALISTIC_VIEWPORTS)
                is_mobile = viewport["width"] < 600
                dpr = 3 if is_mobile else 1
                geo_data = get_ip_geo(valid_proxy)
                user_agent = get_random_user_agent(geo_data)
                
                browser = await p.chromium.launch(
                    headless=False,  # Set headless=True to run in background
                    proxy=proxy_config,
                    args=["--disable-blink-features=AutomationControlled"],  # Hide automation
                )
                context = await browser.new_context(
                    user_agent=user_agent,
                    viewport=viewport,
                    device_scale_factor=dpr,
                    is_mobile=is_mobile,
                    ignore_https_errors=True,
                )
                
                # Generate initial dynamic cookies
                dynamic_cookies = generate_dynamic_cookies()
                await context.add_cookies([
                    {"name": name, "value": value, "domain": "www.profitableratecpm.com", "path": "/"}
                    for name, value in dynamic_cookies.items()
                ])
                logging.info(f"Added initial dynamic cookies for domain: www.profitableratecpm.com")
                
                # Spoof browser fingerprints
                await spoof_fingerprints(context, geo_data)
                
                # Navigate to the target website
                page = await context.new_page()
                await page.goto("https://news-hub-indol.vercel.app/")
                
                # # Mimic human behavior with dynamic cookie updates
                # await mimic_human_behavior(page, context)
                
                await update_cookies(context, "www.profitableratecpm.com")
                
                # Keep the browser open for a while
                await asyncio.sleep(50)
                
                # Cleanup before closing the browser
                logging.info("Cleaning up cookies and storage...")
                await context.clear_cookies()
                await page.evaluate("""
                    try {
                        window.localStorage.clear();
                        window.sessionStorage.clear();
                    } catch (error) {
                        console.warn('Failed to clear localStorage/sessionStorage:', error.message);
                    }
                """)
                logging.info("Cleanup completed.")
                await browser.close()
                logging.info("Browser closed. Restarting...")
        
        except Exception as e:
            logging.error(f"An error occurred: {e}. Restarting browser...")
            continue  # Restart the loop to open a new browser instance
        
        
if __name__ == "__main__":
    asyncio.run(main())
    
    logging.info("Script finished running.")