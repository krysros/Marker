from pyramid.config import Configurator
from pyramid.i18n import default_locale_negotiator
from pyramid.session import SignedCookieSessionFactory

from .security_settings import (
    get_cookie_samesite,
    get_cookie_secure,
    get_validated_secret,
)


def locale_negotiator(request):
    locale = request.cookies.get("_LOCALE_")
    if locale:
        return locale
    return default_locale_negotiator(request)


def main(global_config, **settings):
    """This function returns a Pyramid WSGI application."""
    with Configurator(settings=settings) as config:
        session_factory = SignedCookieSessionFactory(
            get_validated_secret(
                settings,
                setting_key="session.secret",
                env_key="MARKER_SESSION_SECRET",
            ),
            secure=get_cookie_secure(settings),
            httponly=True,
            samesite=get_cookie_samesite(settings),
        )
        config.set_session_factory(session_factory)
        config.set_locale_negotiator(locale_negotiator)
        config.add_subscriber(
            ".subscribers.add_renderer_globals", "pyramid.events.BeforeRender"
        )
        config.add_subscriber(".subscribers.add_localizer", "pyramid.events.NewRequest")
        config.add_translation_dirs("marker:locale")
        config.include(".models")
        config.include(".routes")
        config.include(".security")
        config.scan()
        return config.make_wsgi_app()
