from pyramid.authentication import AuthTktCookieHelper
from pyramid.authorization import ACLHelper, Authenticated, Everyone
from pyramid.csrf import CookieCSRFStoragePolicy
from pyramid.request import RequestLocalCache

from . import models
from .security_settings import (
    get_cookie_samesite,
    get_cookie_secure,
    get_int_setting,
    get_validated_secret,
)


class MySecurityPolicy:
    def __init__(
        self,
        secret,
        *,
        secure=False,
        samesite="Lax",
        timeout=43200,
        reissue_time=1800,
        max_age=43200,
    ):
        self.authtkt = AuthTktCookieHelper(
            secret,
            secure=secure,
            http_only=True,
            timeout=timeout,
            reissue_time=reissue_time,
            max_age=max_age,
            samesite=samesite,
            wild_domain=False,
        )
        self.identity_cache = RequestLocalCache(self.load_identity)
        self.acl = ACLHelper()

    def load_identity(self, request):
        identity = self.authtkt.identify(request)
        if identity is None:
            return None

        userid = identity["userid"]
        user = request.dbsession.get(models.User, userid)
        return user

    def identity(self, request):
        return self.identity_cache.get_or_create(request)

    def authenticated_userid(self, request):
        user = self.identity(request)
        if user is not None:
            return user.id

    def remember(self, request, userid, **kw):
        return self.authtkt.remember(request, userid, **kw)

    def forget(self, request, **kw):
        return self.authtkt.forget(request, **kw)

    def permits(self, request, context, permission):
        principals = self.effective_principals(request)
        return self.acl.permits(context, principals, permission)

    def effective_principals(self, request):
        principals = [Everyone]
        user = self.identity(request)
        if user is not None:
            principals.append(Authenticated)
            principals.append("u:" + str(user.id))
            principals.append("role:" + user.role)
        return principals


def includeme(config):
    settings = config.get_settings()

    cookie_secure = get_cookie_secure(settings)
    cookie_samesite = get_cookie_samesite(settings)

    config.set_csrf_storage_policy(
        CookieCSRFStoragePolicy(
            secure=cookie_secure,
            httponly=True,
            samesite=cookie_samesite,
        )
    )
    config.set_default_csrf_options(require_csrf=True)

    config.set_security_policy(
        MySecurityPolicy(
            get_validated_secret(
                settings,
                setting_key="auth.secret",
                env_key="MARKER_AUTH_SECRET",
            ),
            secure=cookie_secure,
            samesite=cookie_samesite,
            timeout=get_int_setting(settings, "auth.timeout", 43200),
            reissue_time=get_int_setting(settings, "auth.reissue_time", 1800),
            max_age=get_int_setting(settings, "auth.max_age", 43200),
        )
    )
