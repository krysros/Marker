from pyramid.authorization import ALL_PERMISSIONS, Allow, Authenticated


class DefaultResource:
    def __acl__(self):
        return [
            (Allow, Authenticated, "view"),
            (Allow, "role:editor", ("add", "edit")),
            (Allow, "role:admin", ALL_PERMISSIONS),
        ]


class AccountResource:
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


class TagResource(DefaultResource):
    def __init__(self, tag):
        self.tag = tag


class CompanyResource(DefaultResource):
    def __init__(self, company):
        self.company = company


class ContactResource(DefaultResource):
    def __init__(self, contact):
        self.contact = contact


class CommentResource(DefaultResource):
    def __init__(self, comment):
        self.comment = comment


class ProjectResource(DefaultResource):
    def __init__(self, project):
        self.project = project
