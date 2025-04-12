import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import time

PROXY_SOURCES = [
    "https://free-proxy-list.net/",
    "https://www.sslproxies.org/",
    "https://www.us-proxy.org/",
    "https://www.socks-proxy.net/"
]

def scrape_proxies_from_url(url, proxy_types):
    """ گرفتن پراکسی‌ها از یک URL"""
    print(f"[*] دریافت پراکسی از: {url}")
    proxies = []
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", id="proxylisttable")
        for row in table.tbody.find_all("tr"):
            cols = row.find_all("td")
            ip = cols[0].text
            port = cols[1].text
            country = cols[3].text or "Unknown"
            proxy_type = "SOCKS5" if cols[4].text.lower() == "yes" else "HTTP"  # Check SOCKS
            if proxy_type in proxy_types:
                proxies.append({
                    "ip": ip,
                    "port": port,
                    "country": country,
                    "proxy": f"{proxy_type.lower()}://{ip}:{port}",
                    "type": proxy_type
                })
    except Exception as e:
        print(f"[!] خطا هنگام دریافت از {url}: {e}")
    return proxies

def get_all_proxies(proxy_types):
    """ دریافت تمام پراکسی‌ها از منابع مختلف """
    all_proxies = []
    for source in PROXY_SOURCES:
        all_proxies.extend(scrape_proxies_from_url(source, proxy_types))
        time.sleep(1)
    print(f"[+] تعداد کل پراکسی‌های پیدا شده: {len(all_proxies)}")
    return all_proxies

def is_proxy_working(proxy):
    """ بررسی سالم بودن یک پراکسی """
    proxy_url = proxy["proxy"]
    try:
        response = requests.get("http://httpbin.org/ip", proxies={"http": proxy_url, "https": proxy_url}, timeout=6)
        return proxy
    except:
        return None

def collect_valid_proxies_multithread(proxies, min_proxies_per_country):
    """ بررسی سالم بودن پراکسی‌ها و فیلتر کردن بر اساس کشور """
    print("[*] تست پراکسی‌ها به صورت چند نخی...")
    working = defaultdict(list)
    results = []

    with ThreadPoolExecutor(max_workers=50) as executor:
        future_to_proxy = {executor.submit(is_proxy_working, proxy): proxy for proxy in proxies}
        for future in as_completed(future_to_proxy):
            proxy = future_to_proxy[future]
            try:
                result = future.result()
                if result:
                    country = result["country"]
                    if len(working[country]) < min_proxies_per_country:
                        working[country].append(result["proxy"])
                        results.append({
                            "country": country,
                            "proxy": result["proxy"],
                            "type": result["type"]
                        })
                        print(f"[✓] پراکسی سالم از {country} ({len(working[country])})")
            except:
                pass

    return working, results
