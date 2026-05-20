from pyramid.threadlocal import get_current_request


class TranslationString:
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        request = get_current_request()
        if request is not None and hasattr(request, "translate"):
            return request.translate(self.msg)
        return self.msg
