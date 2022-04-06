from pyramid.authorization import (
    Allow,
    Authenticated,
    ALL_PERMISSIONS,
)


class DefaultResource(object):
    def __acl__(self):
        return [
            (Allow, Authenticated, "view"),
            (Allow, "role:editor", ("add", "edit")),
            (Allow, "role:admin", ALL_PERMISSIONS),
        ]


class AccountResource(object):
    def __init__(self, user):
        self.user = user

    def __acl__(self):
        return [
            (Allow, "u:" + str(self.user.id), "view"),
            (Allow, "u:" + str(self.user.id), "edit"),
            (Allow, "role:admin", ALL_PERMISSIONS),
        ]


class UserResource(DefaultResource):
    def __init__(self, user):
        self.user = user

    def __acl__(self):
        return [
            (Allow, "u:" + str(self.user.id), "view"),
            (Allow, "u:" + str(self.user.id), "edit"),
            (Allow, "role:admin", ALL_PERMISSIONS),
        ]


class BranchResource(DefaultResource):
    def __init__(self, branch):
        self.branch = branch


class CompanyResource(DefaultResource):
    def __init__(self, company):
        self.company = company


class PersonResource(DefaultResource):
    def __init__(self, person):
        self.person = person


class CommentResource(DefaultResource):
    def __init__(self, comment):
        self.comment = comment


class TenderResource(DefaultResource):
    def __init__(self, tender):
        self.tender = tender


class DocumentResource(DefaultResource):
    def __init__(self, document):
        self.document = document
