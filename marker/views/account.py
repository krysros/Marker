import logging

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from ..forms import Account, ChangePassword

log = logging.getLogger(__name__)


class AccountView:
    def __init__(self, request):
        self.request = request

    @view_config(route_name="account", renderer="account.mako", permission="edit")
    def account_edit(self):
        _ = self.request.translate
        user = self.request.identity
        form = Account(self.request.POST, user)

        if self.request.method == "POST" and form.validate():
            form.populate_obj(user)
            self.request.session.flash(_("success:Changes have been saved"))
            log.info(_("The user %s has changed his details") % user.name)
            return HTTPFound(location=self.request.current_route_url())
        return {"form": form}

    @view_config(route_name="password", renderer="password.mako", permission="edit")
    def password_edit(self):
        _ = self.request.translate
        user = self.request.identity
        form = ChangePassword(
            self.request.POST, user, meta={"locales": [self.request.locale_name]}
        )

        if self.request.method == "POST" and form.validate():
            form.populate_obj(user)
            self.request.session.flash(_("success:Changes have been saved"))
            log.info(_("The user %s changed the password") % user.name)
            return HTTPFound(location=self.request.current_route_url())
        return {"form": form}
