from .factories import (
    account_factory,
    comment_factory,
    company_factory,
    default_factory,
    contact_factory,
    project_factory,
    tag_factory,
    user_factory,
)


def includeme(config):
    config.add_static_view("static", "static", cache_max_age=3600)
    config.add_route("home", "/")
    config.add_route("login", "/login")
    config.add_route("logout", "/logout")
    config.add_route("theme", "/theme", factory=default_factory)

    config.add_route("account", "/account", factory=account_factory)
    config.add_route("password", "/password", factory=account_factory)

    config.add_route("report", "/report", factory=default_factory)
    config.add_route("report_all", "/report/{rel}", factory=default_factory)
    config.add_route("report_more", "/report/{rel}/more", factory=default_factory)

    config.add_route("tag_all", "/tag", factory=default_factory)
    config.add_route("tag_more", "/tag/more", factory=default_factory)
    config.add_route("tag_count", "/tag/count", factory=default_factory)
    config.add_route(
        "tag_view",
        r"/tag/{tag_id:\d+}/{slug}",
        factory=tag_factory,
    )
    config.add_route(
        "tag_companies_json",
        r"/tag/{tag_id:\d+}/{slug}/companies/json",
        factory=tag_factory,
    )
    config.add_route(
        "tag_projects_json",
        r"/tag/{tag_id:\d+}/{slug}/projects/json",
        factory=tag_factory,
    )
    config.add_route(
        "tag_companies",
        r"/tag/{tag_id:\d+}/{slug}/companies",
        factory=tag_factory,
    )
    config.add_route(
        "tag_companies_more",
        r"/tag/{tag_id:\d+}/{slug}/companies/more",
        factory=tag_factory,
    )
    config.add_route(
        "tag_companies_map",
        r"/tag/{tag_id:\d+}/{slug}/companies/map",
        factory=tag_factory,
    )
    config.add_route(
        "tag_companies_export",
        r"/tag/{tag_id:\d+}/{slug}/companies/export",
        factory=tag_factory,
    )
    config.add_route(
        "count_tag_companies",
        r"/count/tag/{tag_id:\d+}/{slug}/companies",
        factory=tag_factory,
    )
    config.add_route(
        "tag_projects",
        r"/tag/{tag_id:\d+}/{slug}/projects",
        factory=tag_factory,
    )
    config.add_route(
        "tag_projects_more",
        r"/tag/{tag_id:\d+}/{slug}/projects/more",
        factory=tag_factory,
    )
    config.add_route(
        "tag_projects_map",
        r"/tag/{tag_id:\d+}/{slug}/projects/map",
        factory=tag_factory,
    )
    config.add_route(
        "tag_projects_export",
        r"/tag/{tag_id:\d+}/{slug}/projects/export",
        factory=tag_factory,
    )
    config.add_route(
        "count_tag_projects",
        r"/count/tag/{tag_id:\d+}/{slug}/projects",
        factory=tag_factory,
    )
    config.add_route("tag_add", "/tag/add", factory=default_factory)
    config.add_route("tag_search", "/tag/search", factory=default_factory)
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
    config.add_route(
        "delete_tag",
        r"/delete/tag/{tag_id:\d+}/{slug}",
        factory=tag_factory,
    )
    config.add_route(
        "tag_check",
        r"/check/tag/{tag_id:\d+}",
        factory=tag_factory,
    )

    config.add_route("company_all", "/company", factory=default_factory)
    config.add_route("company_more", "/company/more", factory=default_factory)
    config.add_route("company_json", "/company/json", factory=default_factory)
    config.add_route("company_map", "/company/map", factory=default_factory)
    config.add_route("company_add", "/company/add", factory=default_factory)
    config.add_route("company_search", "/company/search", factory=default_factory)
    config.add_route("company_select", "/company/select", factory=default_factory)
    config.add_route("company_count_all", "/company/count", factory=default_factory)
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
        "delete_company",
        r"/delete/company/{company_id:\d+}/{slug}",
        factory=company_factory,
    )
    config.add_route(
        "company_contacts",
        r"/company/{company_id:\d+}/{slug}/contacts",
        factory=company_factory,
    )
    config.add_route(
        "company_tags",
        r"/company/{company_id:\d+}/{slug}/tags",
        factory=company_factory,
    )
    config.add_route(
        "count_company_projects",
        r"/count/company/{company_id:\d+}/{slug}/projects",
        factory=company_factory,
    )
    config.add_route(
        "count_company_tags",
        r"/count/company/{company_id:\d+}/{slug}/tags",
        factory=company_factory,
    )
    config.add_route(
        "count_company_contacts",
        r"/count/company/{company_id:\d+}/{slug}/contacts",
        factory=company_factory,
    )
    config.add_route(
        "count_company_comments",
        r"/count/company/{company_id:\d+}/{slug}/comments",
        factory=company_factory,
    )
    config.add_route(
        "count_company_recommended",
        r"/count/company/{company_id:\d+}/{slug}/recommended",
        factory=company_factory,
    )
    config.add_route(
        "count_company_similar",
        r"/count/company/{company_id:\d+}/{slug}/similar",
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
        "company_recommended",
        r"/company/{company_id:\d+}/{slug}/recommended",
        factory=company_factory,
    )
    config.add_route(
        "company_recommended_more",
        r"/company/{company_id:\d+}/{slug}/recommended/more",
        factory=company_factory,
    )
    config.add_route(
        "company_recommend",
        r"/recommend/company/{company_id:\d+}",
        factory=company_factory,
    )
    config.add_route(
        "company_check",
        r"/check/company/{company_id:\d+}",
        factory=company_factory,
    )
    config.add_route(
        "add_tag_to_company",
        r"/add/company/{company_id:\d+}/{slug}/tag",
        factory=company_factory,
    )
    config.add_route(
        "add_contact_to_company",
        r"/add/company/{company_id:\d+}/{slug}/contact",
        factory=company_factory,
    )
    config.add_route(
        "add_contact_to_project",
        r"/add/project/{project_id:\d+}/{slug}/contact",
        factory=project_factory,
    )
    config.add_route(
        "add_project_to_company",
        r"/add/company/{company_id:\d+}/{slug}/project",
        factory=company_factory,
    )
    config.add_route(
        "add_company_to_project",
        r"/add/project/{project_id:\d+}/{slug}/company",
        factory=project_factory,
    )
    config.add_route(
        "unlink_project",
        r"/unlink/company/{company_id:\d+}/project/{project_id:\d+}",
        factory=default_factory,
    )
    config.add_route(
        "unlink_tag_from_company",
        r"/unlink/company/{company_id:\d+}/tag/{tag_id:\d+}",
        factory=default_factory,
    )

    config.add_route("comment_all", "/comment", factory=default_factory)
    config.add_route("comment_more", "/comment/more", factory=default_factory)
    config.add_route("count_comments", "/count/comments", factory=default_factory)
    config.add_route(
        "comment_company",
        r"/add/comment/company/{company_id:\d+}",
        factory=company_factory,
    )
    config.add_route(
        "comment_project",
        r"/add/comment/project/{project_id:\d+}",
        factory=project_factory,
    )
    config.add_route(
        "comment_delete",
        r"/comment/{comment_id:\d+}/delete",
        factory=comment_factory,
    )
    config.add_route("comment_search", "/comment/search", factory=default_factory)

    config.add_route(
        "contact_vcard",
        r"/contact/{contact_id:\d+}/{slug}/vcard",
        factory=contact_factory,
    )
    config.add_route(
        "contact_view",
        r"/contact/{contact_id:\d+}/{slug}",
        factory=contact_factory,
    )
    config.add_route(
        "contact_edit",
        r"/contact/{contact_id:\d+}/{slug}/edit",
        factory=contact_factory,
    )
    config.add_route(
        "contact_delete",
        r"/contact/{contact_id:\d+}/{slug}/delete",
        factory=contact_factory,
    )
    config.add_route(
        "delete_contact",
        r"/delete/contact/{contact_id:\d+}/{slug}",
        factory=contact_factory,
    )
    config.add_route(
        "contact_check",
        r"/check/contact/{contact_id:\d+}",
        factory=contact_factory,
    )
    config.add_route("contact_all", "/contact", factory=default_factory)
    config.add_route("contact_more", "/contact/more", factory=default_factory)
    config.add_route("contact_search", "/contact/search", factory=default_factory)
    config.add_route("contact_count_all", "/contact/count", factory=default_factory)

    config.add_route("project_all", "/project", factory=default_factory)
    config.add_route("project_more", "/project/more", factory=default_factory)
    config.add_route("project_json", "/project/json", factory=default_factory)
    config.add_route("project_map", "/project/map", factory=default_factory)
    config.add_route("project_add", "/project/add", factory=default_factory)
    config.add_route("project_search", "/project/search", factory=default_factory)
    config.add_route("project_select", "/project/select", factory=default_factory)
    config.add_route("project_count_all", "/project/count", factory=default_factory)
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
        "delete_project",
        r"/delete/project/{project_id:\d+}/{slug}",
        factory=project_factory,
    )
    config.add_route(
        "project_contacts",
        r"/project/{project_id:\d+}/{slug}/contacts",
        factory=project_factory,
    )
    config.add_route(
        "project_tags",
        r"/project/{project_id:\d+}/{slug}/tags",
        factory=project_factory,
    )
    config.add_route(
        "project_comments",
        r"/project/{project_id:\d+}/{slug}/comments",
        factory=project_factory,
    )
    config.add_route(
        "project_comments_more",
        r"/project/{project_id:\d+}/{slug}/comments/more",
        factory=project_factory,
    )
    config.add_route(
        "project_similar",
        r"/project/{project_id:\d+}/{slug}/similar",
        factory=project_factory,
    )
    config.add_route(
        "project_similar_more",
        r"/project/{project_id:\d+}/{slug}/similar/more",
        factory=project_factory,
    )
    config.add_route(
        "project_check",
        r"/check/project/{project_id:\d+}",
        factory=project_factory,
    )
    config.add_route(
        "project_watch",
        r"/watch/project/{project_id:\d+}",
        factory=project_factory,
    )
    config.add_route(
        "project_watched",
        r"/project/{project_id:\d+}/{slug}/watched",
        factory=project_factory,
    )
    config.add_route(
        "project_watched_more",
        r"/project/{project_id:\d+}/{slug}/watched/more",
        factory=project_factory,
    )
    config.add_route(
        "count_project_companies",
        r"/count/project/{project_id:\d+}/{slug}/companies",
        factory=project_factory,
    )
    config.add_route(
        "count_project_tags",
        r"/count/project/{project_id:\d+}/{slug}/tags",
        factory=project_factory,
    )
    config.add_route(
        "count_project_contacts",
        r"/count/project/{project_id:\d+}/{slug}/contacts",
        factory=project_factory,
    )
    config.add_route(
        "count_project_comments",
        r"/count/project/{project_id:\d+}/{slug}/comments",
        factory=project_factory,
    )
    config.add_route(
        "count_project_watched",
        r"/count/project/{project_id:\d+}/{slug}/watched",
        factory=project_factory,
    )
    config.add_route(
        "count_project_similar",
        r"/count/project/{project_id:\d+}/{slug}/similar",
        factory=project_factory,
    )
    config.add_route(
        "add_tag_to_project",
        r"/add/project/{project_id:\d+}/{slug}/tag",
        factory=project_factory,
    )
    config.add_route(
        "unlink_tag_from_project",
        r"/unlink/project/{project_id:\d+}/tag/{tag_id:\d+}",
        factory=default_factory,
    )

    config.add_route("user_all", "/user", factory=default_factory)
    config.add_route("user_more", "/user/more", factory=default_factory)
    config.add_route("user_add", "/user/add", factory=default_factory)
    config.add_route("user_search", "/user/search", factory=default_factory)
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
    config.add_route("user_contacts", "/user/{username}/contacts", factory=user_factory)
    config.add_route(
        "user_contacts_more",
        "/user/{username}/contacts/more",
        factory=user_factory,
    )
    config.add_route(
        "user_selected_companies",
        "/user/{username}/selected_companies",
        factory=user_factory,
    )
    config.add_route(
        "user_selected_companies_more",
        "/user/{username}/selected_companies/more",
        factory=user_factory,
    )
    config.add_route(
        "user_selected_companies_export",
        "/user/{username}/selected_companies/export",
        factory=user_factory,
    )
    config.add_route(
        "user_selected_companies_clear",
        "/user/{username}/selected_companies/clear",
        factory=user_factory,
    )
    config.add_route(
        "user_selected_projects",
        "/user/{username}/selected_projects",
        factory=user_factory,
    )
    config.add_route(
        "user_selected_projects_more",
        "/user/{username}/selected_projects/more",
        factory=user_factory,
    )
    config.add_route(
        "user_selected_projects_export",
        "/user/{username}/selected_projects/export",
        factory=user_factory,
    )
    config.add_route(
        "user_selected_projects_clear",
        "/user/{username}/selected_projects/clear",
        factory=user_factory,
    )
    config.add_route(
        "user_selected_tags",
        "/user/{username}/selected_tags",
        factory=user_factory,
    )
    config.add_route(
        "user_selected_tags_more",
        "/user/{username}/selected_tags/more",
        factory=user_factory,
    )
    config.add_route(
        "user_selected_tags_export",
        "/user/{username}/selected_tags/export",
        factory=user_factory,
    )
    config.add_route(
        "user_selected_tags_clear",
        "/user/{username}/selected_tags/clear",
        factory=user_factory,
    )
    config.add_route(
        "user_selected_contacts",
        "/user/{username}/selected_contacts",
        factory=user_factory,
    )
    config.add_route(
        "user_selected_contacts_more",
        "/user/{username}/selected_contacts/more",
        factory=user_factory,
    )
    config.add_route(
        "user_selected_contacts_export",
        "/user/{username}/selected_contacts/export",
        factory=user_factory,
    )
    config.add_route(
        "user_selected_contacts_clear",
        "/user/{username}/selected_contacts/clear",
        factory=user_factory,
    )
    config.add_route(
        "user_recommended", "/user/{username}/recommended", factory=user_factory
    )
    config.add_route(
        "user_recommended_more",
        "/user/{username}/recommended/more",
        factory=user_factory,
    )
    config.add_route(
        "user_recommended_export",
        "/user/{username}/recommended/export",
        factory=user_factory,
    )
    config.add_route(
        "user_recommended_clear",
        "/user/{username}/recommended/clear",
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
