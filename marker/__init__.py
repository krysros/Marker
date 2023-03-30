from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory


def main(global_config, **settings):
    """This function returns a Pyramid WSGI application."""
    with Configurator(settings=settings) as config:
        session_factory = SignedCookieSessionFactory(settings["session.secret"])
        config.set_session_factory(session_factory)
        config.add_subscriber(
            ".subscribers.add_renderer_globals", "pyramid.events.BeforeRender"
        )
        config.add_subscriber(".subscribers.add_localizer", "pyramid.events.NewRequest")
        config.include(".models")
        config.include(".routes")
        config.include(".security")
        config.scan()
        return config.make_wsgi_app()
