import requests

def test_target_site(proxy_url, target_url):
    """ تست دسترسی به سایت با پراکسی مشخص """
    try:
        response = requests.get(target_url, proxies={"http": proxy_url, "https": proxy_url}, timeout=6)
        return response.status_code
    except:
        return None

def check_sites_with_proxies(target_urls, proxy_list):
    """ بررسی دسترسی سایت‌ها با پراکسی‌های مختلف """
    print(f"\n[*] شروع بررسی لیست سایت‌ها ({len(target_urls)} سایت)...\n")
    results = []
    for url in target_urls:
        print(f"🌐 بررسی دامنه: {url}")
        for entry in proxy_list:
            proxy = entry["proxy"]
            country = entry["country"]
            print(f"  → از {country} با پراکسی {proxy} ... ", end="")
            status = test_target_site(proxy, url)
            if status == 200:
                print("✅ سایت باز شد")
                entry["status"] = "Accessible"
            elif status:
                print(f"⚠️ HTTP {status}")
                entry["status"] = f"HTTP {status}"
            else:
                print("❌ اتصال ناموفق")
                entry["status"] = "Failed"
            results.append({
                "target": url,
                "country": country,
                "proxy": proxy,
                "status": entry["status"]
            })
            # Optional: You can add sleep time to avoid overloading servers
    return results
