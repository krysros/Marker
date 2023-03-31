from pyramid.threadlocal import get_current_request


class TranslationString:
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        request = get_current_request()
        return request.translate(self.msg)
