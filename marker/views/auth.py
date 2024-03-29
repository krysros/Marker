import logging

from pyramid.csrf import new_csrf_token
from pyramid.httpexceptions import HTTPException, HTTPSeeOther
from pyramid.renderers import render_to_response
from pyramid.security import forget, remember
from pyramid.view import forbidden_view_config, view_config
from sqlalchemy import select

from ..forms import LoginForm
from ..models import User

log = logging.getLogger(__name__)


@view_config(route_name="login", renderer="login.mako")
def login(request):
    _ = request.translate
    next_url = request.params.get("next")
    if not next_url:
        next_url = request.route_url("home")

    form = LoginForm(request.POST)

    if request.method == "POST" and form.validate():
        username = form.username.data
        password = form.password.data
        user = request.dbsession.execute(
            select(User).filter_by(name=username)
        ).scalar_one_or_none()
        if user is not None and user.check_password(password):
            new_csrf_token(request)
            headers = remember(request, user.id)
            request.session.flash(_("success:Hello!"))
            log.info(_("The user %s has logged in") % user.name)
            return HTTPSeeOther(location=next_url, headers=headers)
        request.response.status = 400
        request.session.flash(_("danger:Login failed"))
    return {
        "url": request.route_url("login"),
        "next_url": next_url,
        "heading": _("Log in"),
        "form": form,
    }


@view_config(route_name="logout")
def logout(request):
    _ = request.translate
    next_url = request.route_url("home")
    if request.method == "POST":
        new_csrf_token(request)
        headers = forget(request)
        request.session.flash(_("success:Logged out"))
        log.info(_("The user %s has logged out") % request.identity.name)
        return HTTPSeeOther(location=next_url, headers=headers)
    return HTTPSeeOther(location=next_url)


@forbidden_view_config()
def forbidden(exc, request):
    _ = request.translate
    if not request.is_authenticated:
        next_url = request.route_url("login", _query={"next": request.url})
        request.session.flash(_("warning:No required permissions"))
        return HTTPSeeOther(location=next_url)
    return httpexception_view(exc, request)


@view_config(context=HTTPException)
def httpexception_view(exc, request):
    # This function is based on the function of the same name from the module:
    # https://github.com/pypi/warehouse/blob/9e853ac20cdce3df43acb07541c3f78ebdd811a0/warehouse/views.py#L74
    try:
        response = render_to_response(f"{exc.status_code}.mako", {}, request=request)
    except LookupError:
        return exc

    # Copy over the important values from our HTTPException to our new response
    # object.
    response.status = exc.status
    response.headers.extend(
        (k, v) for k, v in exc.headers.items() if k not in response.headers
    )

    return response
