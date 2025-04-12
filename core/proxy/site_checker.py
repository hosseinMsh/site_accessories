import requests

def test_target_site(proxy_url, target_url):
    """ Test access to a site using a specific proxy """
    try:
        response = requests.get(target_url, proxies={"http": proxy_url, "https": proxy_url}, timeout=6)
        return response.status_code
    except:
        return None

def check_sites_with_proxies(target_urls, proxy_list):
    """ Check accessibility of sites using different proxies """
    print(f"\n[*] Starting to check the list of sites ({len(target_urls)} sites)...\n")
    results = []
    for url in target_urls:
        print(f"🌐 Checking domain: {url}")
        for entry in proxy_list:
            proxy = entry["proxy"]
            country = entry["country"]
            print(f"  → From {country} with proxy {proxy} ... ", end="")
            status = test_target_site(proxy, url)
            if status == 200:
                print("✅ Site is accessible")
                entry["status"] = "Accessible"
            elif status:
                print(f"⚠️ HTTP {status}")
                entry["status"] = f"HTTP {status}"
            else:
                print("❌ Connection failed")
                entry["status"] = "Failed"
            results.append({
                "target": url,
                "country": country,
                "proxy": proxy,
                "status": entry["status"]
            })
            # Optional: You can add sleep time to avoid overloading servers
    return results
