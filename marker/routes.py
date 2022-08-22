from .factories import (
    default_factory,
    account_factory,
    tag_factory,
    company_factory,
    comment_factory,
    person_factory,
    project_factory,
    user_factory,
)


def includeme(config):
    config.add_static_view("static", "static", cache_max_age=3600)
    config.add_route("home", "/")
    config.add_route("login", "/login")
    config.add_route("logout", "/logout")

    config.add_route("account", "/account", factory=account_factory)
    config.add_route("password", "/password", factory=account_factory)

    config.add_route("report", "/report", factory=default_factory)
    config.add_route("report_results", "/report/{rel}", factory=default_factory)
    config.add_route("report_more", "/report/{rel}/more", factory=default_factory)

    config.add_route("tag_all", "/tag", factory=default_factory)
    config.add_route("tag_more", "/tag/more", factory=default_factory)
    config.add_route(
        "tag_view",
        r"/tag/{tag_id:\d+}/{slug}/companies",
        factory=tag_factory,
    )
    config.add_route(
        "tag_view_more",
        r"/tag/{tag_id:\d+}/{slug}/companies/more",
        factory=tag_factory,
    )
    config.add_route(
        "tag_export",
        r"/tag/{tag_id:\d+}/export",
        factory=tag_factory,
    )
    config.add_route("tag_add", "/tag/add", factory=default_factory)
    config.add_route("tag_search", "/tag/search", factory=default_factory)
    config.add_route("tag_results", "/tag/results", factory=default_factory)
    config.add_route("tag_results_more", "/tag/results/more", factory=default_factory)
    config.add_route("tag_select", "/tag/select", factory=default_factory)
    config.add_route(
        "tag_edit",
        r"/tag/{tag_id:\d+}/{slug}/edit",
        factory=tag_factory,
    )
    config.add_route(
        "tag_delete",
        r"/tag/{tag_id:\d+}/{slug}/delete",
        factory=tag_factory,
    )

    config.add_route("company_all", "/company", factory=default_factory)
    config.add_route("company_more", "/company/more", factory=default_factory)
    config.add_route("company_add", "/company/add", factory=default_factory)
    config.add_route("company_search", "/company/search", factory=default_factory)
    config.add_route("company_results", "/company/results", factory=default_factory)
    config.add_route(
        "company_results_more",
        "/company/results/more",
        factory=default_factory,
    )
    config.add_route("company_select", "/company/select", factory=default_factory)
    config.add_route(
        "company_view",
        r"/company/{company_id:\d+}/{slug}",
        factory=company_factory,
    )
    config.add_route(
        "company_edit",
        r"/company/{company_id:\d+}/{slug}/edit",
        factory=company_factory,
    )
    config.add_route(
        "company_delete",
        r"/company/{company_id:\d+}/{slug}/delete",
        factory=company_factory,
    )
    config.add_route(
        "company_comments",
        r"/company/{company_id:\d+}/{slug}/comments",
        factory=company_factory,
    )
    config.add_route(
        "company_comments_more",
        r"/company/{company_id:\d+}/{slug}/comments/more",
        factory=company_factory,
    )
    config.add_route(
        "company_projects",
        r"/company/{company_id:\d+}/{slug}/projects",
        factory=company_factory,
    )
    config.add_route(
        "project_companies",
        r"/project/{project_id:\d+}/{slug}/companies",
        factory=project_factory,
    )
    config.add_route(
        "add_project",
        r"/company/{company_id:\d+}/{slug}/projects-table",
        factory=company_factory,
    )
    config.add_route(
        "company_similar",
        r"/company/{company_id:\d+}/{slug}/similar",
        factory=company_factory,
    )
    config.add_route(
        "company_similar_more",
        r"/company/{company_id:\d+}/{slug}/similar/more",
        factory=company_factory,
    )
    config.add_route(
        "company_recomended",
        r"/company/{company_id:\d+}/{slug}/recomended",
        factory=company_factory,
    )
    config.add_route(
        "company_recomended_more",
        r"/company/{company_id:\d+}/{slug}/recomended/more",
        factory=company_factory,
    )
    config.add_route(
        "company_recommend",
        r"/recomend/company/{company_id:\d+}",
        factory=company_factory,
    )
    config.add_route(
        "company_check",
        r"/check/company/{company_id:\d+}",
        factory=company_factory,
    )
    config.add_route(
        "company_tags",
        r"/company/{company_id:\d+}/{slug}/tags",
        factory=company_factory,
    )
    config.add_route(
        "company_people",
        r"/company/{company_id:\d+}/{slug}/people",
        factory=company_factory,
    )
    config.add_route(
        "delete_project",
        r"/company/{company_id:\d+}/project/{project_id:\d+}/delete",
        factory=default_factory,
    )
    config.add_route(
        "delete_tag",
        r"/company/{company_id:\d+}/tag/{tag_id:\d+}/delete",
        factory=default_factory,
    )

    config.add_route("comment_all", "/comment", factory=default_factory)
    config.add_route("comment_more", "/comment/more", factory=default_factory)
    config.add_route(
        "comment_add",
        r"/company/{company_id:\d+}/comment/add",
        factory=company_factory,
    )
    config.add_route(
        "comment_delete",
        r"/comment/{comment_id:\d+}/delete",
        factory=comment_factory,
    )
    config.add_route("comment_search", "/comment/search", factory=default_factory)
    config.add_route("comment_results", "/comment/results", factory=default_factory)
    config.add_route(
        "comment_results_more",
        "/comment/results/more",
        factory=default_factory,
    )

    config.add_route(
        "person_vcard",
        r"/person/{person_id:\d+}/vcard",
        factory=person_factory,
    )
    config.add_route(
        "person_delete",
        r"/person/{person_id:\d+}/delete",
        factory=person_factory,
    )
    config.add_route("person_all", "/person", factory=default_factory)
    config.add_route("person_more", "/person/more", factory=default_factory)
    config.add_route("person_search", "/person/search", factory=default_factory)
    config.add_route("person_results", "/person/results", factory=default_factory)
    config.add_route(
        "person_results_more", "/person/results/more", factory=default_factory
    )

    config.add_route("project_all", "/project", factory=default_factory)
    config.add_route("project_more", "/project/more", factory=default_factory)
    config.add_route("project_add", "/project/add", factory=default_factory)
    config.add_route("project_search", "/project/search", factory=default_factory)
    config.add_route("project_results", "/project/results", factory=default_factory)
    config.add_route(
        "project_results_more",
        "/project/results/more",
        factory=default_factory,
    )
    config.add_route(
        "project_view",
        r"/project/{project_id:\d+}/{slug}",
        factory=project_factory,
    )
    config.add_route(
        "project_edit",
        r"/project/{project_id:\d+}/{slug}/edit",
        factory=project_factory,
    )
    config.add_route(
        "project_delete",
        r"/project/{project_id:\d+}/{slug}/delete",
        factory=project_factory,
    )
    config.add_route(
        "project_watch",
        r"/watch/project/{project_id:\d+}",
        factory=project_factory,
    )
    config.add_route(
        "add_company",
        r"/project/{project_id:\d+}/{slug}/companies-table",
        factory=project_factory,
    )
    config.add_route("project_select", "/project/select", factory=default_factory)

    config.add_route("user_all", "/user", factory=default_factory)
    config.add_route("user_more", "/user/more", factory=default_factory)
    config.add_route("user_add", "/user/add", factory=default_factory)
    config.add_route("user_search", "/user/search", factory=default_factory)
    config.add_route("user_results", "/user/results", factory=default_factory)
    config.add_route("user_results_more", "/user/results/more", factory=default_factory)
    config.add_route("user_view", "/user/{username}", factory=user_factory)
    config.add_route("user_edit", "/user/{username}/edit", factory=user_factory)
    config.add_route("user_delete", "/user/{username}/delete", factory=user_factory)
    config.add_route("user_comments", "/user/{username}/comments", factory=user_factory)
    config.add_route(
        "user_comments_more",
        "/user/{username}/comments/more",
        factory=user_factory,
    )
    config.add_route("user_tags", "/user/{username}/tags", factory=user_factory)
    config.add_route(
        "user_tags_more",
        "/user/{username}/tags/more",
        factory=user_factory,
    )
    config.add_route(
        "user_companies", "/user/{username}/companies", factory=user_factory
    )
    config.add_route(
        "user_companies_more",
        "/user/{username}/companies/more",
        factory=user_factory,
    )
    config.add_route(
        "user_projects",
        "/user/{username}/projects",
        factory=user_factory,
    )
    config.add_route(
        "user_projects_more",
        "/user/{username}/projects/more",
        factory=user_factory,
    )
    config.add_route("user_checked", "/user/{username}/checked", factory=user_factory)
    config.add_route(
        "user_checked_more",
        "/user/{username}/checked/more",
        factory=user_factory,
    )
    config.add_route(
        "user_checked_export",
        "/user/{username}/checked/export",
        factory=user_factory,
    )
    config.add_route(
        "user_checked_clear",
        "/user/{username}/checked/clear",
        factory=user_factory,
    )
    config.add_route(
        "user_recomended", "/user/{username}/recomended", factory=user_factory
    )
    config.add_route(
        "user_recomended_more",
        "/user/{username}/recomended/more",
        factory=user_factory,
    )
    config.add_route(
        "user_recomended_export",
        "/user/{username}/recomended/export",
        factory=user_factory,
    )
    config.add_route(
        "user_recomended_clear",
        "/user/{username}/recomended/clear",
        factory=user_factory,
    )
    config.add_route("user_watched", "/user/{username}/watched", factory=user_factory)
    config.add_route(
        "user_watched_more",
        "/user/{username}/watched/more",
        factory=user_factory,
    )
    config.add_route(
        "user_watched_export",
        "/user/{username}/watched/export",
        factory=user_factory,
    )
    config.add_route(
        "user_watched_clear",
        "/user/{username}/watched/clear",
        factory=user_factory,
    )
