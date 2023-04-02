from pyramid.i18n import TranslationStringFactory, get_localizer


def add_renderer_globals(event):
    request = event["request"]
    event["_"] = request.translate
    event["localizer"] = request.localizer


tsf = TranslationStringFactory("Marker")


def add_localizer(event):
    request = event.request
    localizer = get_localizer(request)

    def auto_translate(*args, **kwargs):
        return localizer.translate(tsf(*args, **kwargs))

    request.localizer = localizer
    request.translate = auto_translate
