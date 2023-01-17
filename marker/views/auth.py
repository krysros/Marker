import logging

from mako.exceptions import TopLevelLookupException
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
            request.session.flash("success:Witaj!")
            log.info(f"Użytkownik {user.name} zalogował się")
            return HTTPSeeOther(location=next_url, headers=headers)
        request.response.status = 400
        request.session.flash("danger:Logowanie nie powiodło się")
    return {
        "url": request.route_url("login"),
        "next_url": next_url,
        "heading": "Zaloguj się",
        "form": form,
    }


@view_config(route_name="logout")
def logout(request):
    next_url = request.route_url("home")
    if request.method == "POST":
        new_csrf_token(request)
        headers = forget(request)
        request.session.flash("success:Wylogowano")
        log.info(f"Użytkownik {request.identity.name} wylogował się")
        return HTTPSeeOther(location=next_url, headers=headers)
    return HTTPSeeOther(location=next_url)


@forbidden_view_config()
def forbidden(exc, request):
    if not request.is_authenticated:
        next_url = request.route_url("login", _query={"next": request.url})
        request.session.flash("warning:Brak wymaganych uprawnień")
        return HTTPSeeOther(location=next_url)
    return httpexception_view(exc, request)


@view_config(context=HTTPException)
def httpexception_view(exc, request):
    try:
        response = render_to_response(f"{exc.status_code}.mako", {}, request=request)
    except TopLevelLookupException:
        return exc
    return response
