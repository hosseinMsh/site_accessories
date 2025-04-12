from django.http import JsonResponse
from django.shortcuts import render

from core.proxy.utils import get_all_proxies, collect_valid_proxies_multithread
from core.proxy.site_checker import check_sites_with_proxies

def check_sites():
    proxy_types = ['HTTP', 'HTTPS', 'SOCKS5']
    proxies = get_all_proxies(proxy_types)
    valid_proxies_dict, valid_proxies = collect_valid_proxies_multithread(proxies, min_proxies_per_country=5)

    target_urls = ['https://sharif.ir', 'https://google.com']
    results = check_sites_with_proxies(target_urls, valid_proxies)

    return JsonResponse({'results': results})