from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt

from core.proxy.utils import get_all_proxies, collect_valid_proxies_multithread
from core.proxy.site_checker import check_sites_with_proxies


@csrf_exempt  # Optional, for testing via tools like Postman
@require_GET  # Only allow GET requests
def check_sites(request):
    """
    View to check access to specific sites using valid proxies.
    """
    proxy_types = ['HTTP', 'HTTPS', 'SOCKS5']
    target_urls = ['https://sharif.ir', 'https://google.com']

    try:
        # Step 1: Gather all proxies
        proxies = get_all_proxies(proxy_types)

        # Step 2: Filter valid proxies
        valid_proxy_map, valid_proxies = collect_valid_proxies_multithread(proxies, min_proxies_per_country=5)

        if not valid_proxies:
            return JsonResponse({'error': 'No valid proxies found.'}, status=503)

        # Step 3: Test target URLs with working proxies
        results = check_sites_with_proxies(target_urls, valid_proxies)

        return JsonResponse({'results': results})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
