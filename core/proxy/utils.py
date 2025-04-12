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

def get_country_by_ip(ip):
    """Use ip-api.com to get the country of an IP"""
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}?fields=country", timeout=5)
        data = res.json()
        return data.get("country", "Unknown")
    except:
        return "Unknown"

def scrape_proxies_from_url(url, proxy_types):
    """Fetch proxies from a given URL"""
    print(f"[*] Fetching proxies from: {url}")
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
            proxy_type = "SOCKS5" if cols[4].text.lower() == "yes" else "HTTP"
            if proxy_type in proxy_types:
                proxies.append({
                    "ip": ip,
                    "port": port,
                    "country": country,
                    "proxy": f"{proxy_type.lower()}://{ip}:{port}",
                    "type": proxy_type
                })
    except Exception as e:
        print(f"[!] Error while fetching from {url}: {e}")
    return proxies

def get_proxyscrape_proxies(proxy_types):
    """Fetch proxies from ProxyScrape API and resolve their countries"""
    proxies = []
    print("[*] Fetching proxies from ProxyScrape API...")

    type_map = {
        "HTTP": "http",
        "SOCKS4": "socks4",
        "SOCKS5": "socks5"
    }

    for p_type in proxy_types:
        if p_type not in type_map:
            continue
        url = f"https://proxy.scrape.do/api/proxy-list?type={type_map[p_type].lower()}&timeout=5000&limit=50&anonymity=all"
        try:
            response = requests.get(url, timeout=10)
            lines = response.text.strip().splitlines()
            for line in lines:
                ip_port = line.strip()
                ip, port = ip_port.split(":")
                country = get_country_by_ip(ip)
                proxies.append({
                    "ip": ip,
                    "port": port,
                    "country": country,
                    "proxy": f"{p_type.lower()}://{ip_port}",
                    "type": p_type
                })
        except Exception as e:
            print(f"[!] Error fetching from ProxyScrape ({p_type}): {e}")
    return proxies

def get_all_proxies(proxy_types):
    """Retrieve all proxies from multiple sources"""
    all_proxies = []

    for source in PROXY_SOURCES:
        all_proxies.extend(scrape_proxies_from_url(source, proxy_types))
        time.sleep(1)

    all_proxies.extend(get_proxyscrape_proxies(proxy_types))

    print(f"[+] Total proxies found: {len(all_proxies)}")
    return all_proxies

def is_proxy_working(proxy):
    """Check if a proxy is working"""
    proxy_url = proxy["proxy"]
    try:
        response = requests.get("http://httpbin.org/ip", proxies={"http": proxy_url, "https": proxy_url}, timeout=6)
        return proxy
    except:
        return None

def collect_valid_proxies_multithread(proxies, min_proxies_per_country):
    """Test proxies using multithreading and filter based on country"""
    print("[*] Testing proxies with multithreading...")
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
                        print(f"[✓] Working proxy from {country} ({len(working[country])})")
            except:
                pass

    return working, results
