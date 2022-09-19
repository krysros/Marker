import logging
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from ..forms import Account
from ..forms import ChangePassword


log = logging.getLogger(__name__)


class AccountView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name="account", renderer="account.mako", permission="edit")
    def account_edit(self):
        user = self.request.identity
        form = Account(self.request.POST, user)

        if self.request.method == "POST" and form.validate():
            form.populate_obj(user)
            # self.request.session.flash("success:Zmiany zostały zapisane")
            log.info(f"Użytkownik {user.name} zmienił swoje dane")
            return HTTPFound(location=self.request.current_route_url())

        return dict(
            heading="Dane użytkownika",
            form=form,
        )

    @view_config(route_name="password", renderer="password.mako", permission="edit")
    def password_edit(self):
        user = self.request.identity
        form = ChangePassword(self.request.POST, user)

        if self.request.method == "POST" and form.validate():
            form.populate_obj(user)
            # self.request.session.flash("success:Zmiany zostały zapisane")
            log.info(f"Użytkownik {user.name} zmienił hasło")
            return HTTPFound(location=self.request.current_route_url())

        return dict(
            heading="Zmiana hasła",
            form=form,
        )
