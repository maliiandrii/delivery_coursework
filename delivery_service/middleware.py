class LanguageMiddleware:
    """
    Middleware that adds support for language codes.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'set_language' in request.GET:
            lang = request.GET['set_language']
            if lang in ['en', 'uk']:
                request.session['language'] = lang
        response = self.get_response(request)
        return response
