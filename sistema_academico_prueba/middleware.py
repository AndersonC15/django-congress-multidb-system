# middleware.py
class LogRealIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Cloudflare envía la IP real en este encabezado
        ip_real = request.META.get('HTTP_CF_CONNECTING_IP')
        
        # Si no es Cloudflare, intenta con X-Forwarded-For
        if not ip_real:
            ip_real = request.META.get('HTTP_X_FORWARDED_FOR')
            
        if ip_real:
            print(f"👀 VISITA DETECTADA DESDE IP: {ip_real} --> {request.path}")
        
        response = self.get_response(request)
        return response