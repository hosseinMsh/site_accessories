from django.http import JsonResponse
from django.shortcuts import render

# وارد کردن ماژول‌ها از مسیر درست
from core.proxy.utils import get_all_proxies, collect_valid_proxies_multithread
from core.proxy.site_checker import check_sites_with_proxies


def check_sites(request):
    # تعیین انواع پراکسی
    proxy_types = ['HTTP', 'HTTPS', 'SOCKS5']

    # دریافت تمام پراکسی‌ها
    proxies = get_all_proxies(proxy_types)

    # فیلتر کردن پراکسی‌های سالم و اعتبارسنجی آن‌ها
    valid_proxies_dict, valid_proxies = collect_valid_proxies_multithread(proxies, min_proxies_per_country=5)

    # تعیین سایت‌های هدف برای تست
    target_urls = ['https://sharif.ir', 'https://google.com']

    # بررسی دسترسی سایت‌ها
    results = check_sites_with_proxies(target_urls, valid_proxies)

    # بازگشت داده‌ها به صورت JSON
    return JsonResponse({'results': results})
