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

    config.add_route("company_all", "/company", factory=default_factory)
    config.add_route("company_more", "/company/more", factory=default_factory)
    config.add_route("company_json", "/company/json", factory=default_factory)
    config.add_route("company_map", "/company/map", factory=default_factory)
    config.add_route("company_add", "/company/add", factory=default_factory)
    config.add_route("company_search", "/company/search", factory=default_factory)
    config.add_route("company_select", "/company/select", factory=default_factory)
    config.add_route("company_count", "/company/count", factory=default_factory)
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
        "company_del_row",
        r"/company/{company_id:\d+}/{slug}/del_row",
        factory=company_factory,
    )
    config.add_route(
        "company_projects",
        r"/company/{company_id:\d+}/{slug}/projects",
        factory=company_factory,
    )
    config.add_route(
        "company_tags",
        r"/company/{company_id:\d+}/{slug}/tags",
        factory=company_factory,
    )
    config.add_route(
        "company_contacts",
        r"/company/{company_id:\d+}/{slug}/contacts",
        factory=company_factory,
    )
    config.add_route(
        "company_comments",
        r"/company/{company_id:\d+}/{slug}/comments",
        factory=company_factory,
    )
    config.add_route(
        "company_more_comments",
        r"/company/{company_id:\d+}/{slug}/more_comments",
        factory=company_factory,
    )
    config.add_route(
        "company_recommended",
        r"/company/{company_id:\d+}/{slug}/recommended",
        factory=company_factory,
    )
    config.add_route(
        "company_more_recommended",
        r"/company/{company_id:\d+}/{slug}/more_recommended",
        factory=company_factory,
    )
    config.add_route(
        "company_similar",
        r"/company/{company_id:\d+}/{slug}/similar",
        factory=company_factory,
    )
    config.add_route(
        "company_more_similar",
        r"/company/{company_id:\d+}/{slug}/more_similar",
        factory=company_factory,
    )
    config.add_route(
        "company_count_projects",
        r"/company/{company_id:\d+}/{slug}/count_projects",
        factory=company_factory,
    )
    config.add_route(
        "company_count_tags",
        r"/company/{company_id:\d+}/{slug}/count_tags",
        factory=company_factory,
    )
    config.add_route(
        "company_count_contacts",
        r"/company/{company_id:\d+}/{slug}/count_contacts",
        factory=company_factory,
    )
    config.add_route(
        "company_count_comments",
        r"/company/{company_id:\d+}/{slug}/count_comments",
        factory=company_factory,
    )
    config.add_route(
        "company_count_recommended",
        r"/company/{company_id:\d+}/{slug}/count_recommended",
        factory=company_factory,
    )
    config.add_route(
        "company_count_similar",
        r"/company/{company_id:\d+}/{slug}/count_similar",
        factory=company_factory,
    )
    config.add_route(
        "company_recommend",
        r"/company/{company_id:\d+}/{slug}/recommend",
        factory=company_factory,
    )
    config.add_route(
        "company_check",
        r"/company/{company_id:\d+}/{slug}/check",
        factory=company_factory,
    )
    config.add_route(
        "add_tag_to_company",
        r"/company/{company_id:\d+}/{slug}/add_tag",
        factory=company_factory,
    )
    config.add_route(
        "add_project_to_company",
        r"/company/{company_id:\d+}/{slug}/add_project",
        factory=company_factory,
    )
    config.add_route(
        "add_contact_to_company",
        r"/company/{company_id:\d+}/{slug}/add_contact",
        factory=company_factory,
    )
    config.add_route(
        "add_comment_to_company",
        r"/company/{company_id:\d+}/{slug}/add_comment",
        factory=company_factory,
    )
    config.add_route(
        "unlink_company_project",
        r"/unlink/company/{company_id:\d+}/project/{project_id:\d+}",
        factory=default_factory,
    )

    config.add_route("project_all", "/project", factory=default_factory)
    config.add_route("project_more", "/project/more", factory=default_factory)
    config.add_route("project_json", "/project/json", factory=default_factory)
    config.add_route("project_map", "/project/map", factory=default_factory)
    config.add_route("project_add", "/project/add", factory=default_factory)
    config.add_route("project_search", "/project/search", factory=default_factory)
    config.add_route("project_select", "/project/select", factory=default_factory)
    config.add_route("project_count", "/project/count", factory=default_factory)
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
        "project_del_row",
        r"/project/{project_id:\d+}/{slug}/del_row",
        factory=project_factory,
    )
    config.add_route(
        "project_companies",
        r"/project/{project_id:\d+}/{slug}/companies",
        factory=project_factory,
    )
    config.add_route(
        "project_tags",
        r"/project/{project_id:\d+}/{slug}/tags",
        factory=project_factory,
    )
    config.add_route(
        "project_contacts",
        r"/project/{project_id:\d+}/{slug}/contacts",
        factory=project_factory,
    )
    config.add_route(
        "project_comments",
        r"/project/{project_id:\d+}/{slug}/comments",
        factory=project_factory,
    )
    config.add_route(
        "project_more_comments",
        r"/project/{project_id:\d+}/{slug}/more_comments",
        factory=project_factory,
    )
    config.add_route(
        "project_watched",
        r"/project/{project_id:\d+}/{slug}/watched",
        factory=project_factory,
    )
    config.add_route(
        "project_more_watched",
        r"/project/{project_id:\d+}/{slug}/more_watched",
        factory=project_factory,
    )
    config.add_route(
        "project_similar",
        r"/project/{project_id:\d+}/{slug}/similar",
        factory=project_factory,
    )
    config.add_route(
        "project_more_similar",
        r"/project/{project_id:\d+}/{slug}/more_similar",
        factory=project_factory,
    )
    config.add_route(
        "project_count_companies",
        r"/project/{project_id:\d+}/{slug}/count_companies",
        factory=project_factory,
    )
    config.add_route(
        "project_count_tags",
        r"/project/{project_id:\d+}/{slug}/count_tags",
        factory=project_factory,
    )
    config.add_route(
        "project_count_contacts",
        r"/project/{project_id:\d+}/{slug}/count_contacts",
        factory=project_factory,
    )
    config.add_route(
        "project_count_comments",
        r"/count/project/{project_id:\d+}/{slug}/count_comments",
        factory=project_factory,
    )
    config.add_route(
        "project_count_watched",
        r"/project/{project_id:\d+}/{slug}/count_watched",
        factory=project_factory,
    )
    config.add_route(
        "project_count_similar",
        r"/project/{project_id:\d+}/{slug}/count_similar",
        factory=project_factory,
    )
    config.add_route(
        "project_check",
        r"/project/{project_id:\d+}/{slug}/check",
        factory=project_factory,
    )
    config.add_route(
        "project_watch",
        r"/project/{project_id:\d+}/{slug}/watch",
        factory=project_factory,
    )
    config.add_route(
        "add_tag_to_project",
        r"/project/{project_id:\d+}/{slug}/add_tag",
        factory=project_factory,
    )
    config.add_route(
        "add_company_to_project",
        r"/project/{project_id:\d+}/{slug}/add_company",
        factory=project_factory,
    )
    config.add_route(
        "add_contact_to_project",
        r"/project/{project_id:\d+}/{slug}/add_contact",
        factory=project_factory,
    )
    config.add_route(
        "add_comment_to_project",
        r"/project/{project_id:\d+}/{slug}/add_comment",
        factory=project_factory,
    )

    config.add_route("tag_all", "/tag", factory=default_factory)
    config.add_route("tag_more", "/tag/more", factory=default_factory)
    config.add_route("tag_count", "/tag/count", factory=default_factory)
    config.add_route("tag_add", "/tag/add", factory=default_factory)
    config.add_route("tag_search", "/tag/search", factory=default_factory)
    config.add_route("tag_select", "/tag/select", factory=default_factory)
    config.add_route(
        "tag_view",
        r"/tag/{tag_id:\d+}/{slug}",
        factory=tag_factory,
    )
    config.add_route(
        "tag_json_companies",
        r"/tag/{tag_id:\d+}/{slug}/json_companies",
        factory=tag_factory,
    )
    config.add_route(
        "tag_json_projects",
        r"/tag/{tag_id:\d+}/{slug}/json_projects",
        factory=tag_factory,
    )
    config.add_route(
        "tag_companies",
        r"/tag/{tag_id:\d+}/{slug}/companies",
        factory=tag_factory,
    )
    config.add_route(
        "tag_more_companies",
        r"/tag/{tag_id:\d+}/{slug}/more_companies",
        factory=tag_factory,
    )
    config.add_route(
        "tag_map_companies",
        r"/tag/{tag_id:\d+}/{slug}/map_companies",
        factory=tag_factory,
    )
    config.add_route(
        "tag_export_companies",
        r"/tag/{tag_id:\d+}/{slug}/export_companies",
        factory=tag_factory,
    )
    config.add_route(
        "tag_count_companies",
        r"/tag/{tag_id:\d+}/{slug}/count_companies",
        factory=tag_factory,
    )
    config.add_route(
        "tag_projects",
        r"/tag/{tag_id:\d+}/{slug}/projects",
        factory=tag_factory,
    )
    config.add_route(
        "tag_more_projects",
        r"/tag/{tag_id:\d+}/{slug}/more_projects",
        factory=tag_factory,
    )
    config.add_route(
        "tag_map_projects",
        r"/tag/{tag_id:\d+}/{slug}/map_projects",
        factory=tag_factory,
    )
    config.add_route(
        "tag_export_projects",
        r"/tag/{tag_id:\d+}/{slug}/export_projects",
        factory=tag_factory,
    )
    config.add_route(
        "tag_count_projects",
        r"/tag/{tag_id:\d+}/{slug}/count_projects",
        factory=tag_factory,
    )
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
        "tag_del_row",
        r"/tag/{tag_id:\d+}/{slug}/del_row",
        factory=tag_factory,
    )
    config.add_route(
        "tag_check",
        r"/tag/{tag_id:\d+}/{slug}/check",
        factory=tag_factory,
    )
    config.add_route(
        "unlink_tag_from_company",
        r"/unlink/tag/{tag_id:\d+}/company/{company_id:\d+}",
        factory=default_factory,
    )
    config.add_route(
        "unlink_tag_from_project",
        r"/unlink/tag/{tag_id:\d+}/project/{project_id:\d+}",
        factory=default_factory,
    )

    config.add_route("contact_all", "/contact", factory=default_factory)
    config.add_route("contact_more", "/contact/more", factory=default_factory)
    config.add_route("contact_search", "/contact/search", factory=default_factory)
    config.add_route("contact_count", "/contact/count", factory=default_factory)
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
        "contact_del_row",
        r"/contact/{contact_id:\d+}/{slug}/del_row",
        factory=contact_factory,
    )
    config.add_route(
        "contact_vcard",
        r"/contact/{contact_id:\d+}/{slug}/vcard",
        factory=contact_factory,
    )
    config.add_route(
        "contact_check",
        r"/contact/{contact_id:\d+}/{slug}/check",
        factory=contact_factory,
    )

    config.add_route("comment_all", "/comment", factory=default_factory)
    config.add_route("comment_more", "/comment/more", factory=default_factory)
    config.add_route("comment_search", "/comment/search", factory=default_factory)
    config.add_route("comment_count", "/comment/count", factory=default_factory)
    config.add_route(
        "comment_delete",
        r"/comment/{comment_id:\d+}/delete",
        factory=comment_factory,
    )

    config.add_route("report", "/report", factory=default_factory)
    config.add_route("report_all", "/report/{rel}", factory=default_factory)
    config.add_route("report_more", "/report/{rel}/more", factory=default_factory)

    config.add_route("user_all", "/user", factory=default_factory)
    config.add_route("user_more", "/user/more", factory=default_factory)
    config.add_route("user_add", "/user/add", factory=default_factory)
    config.add_route("user_search", "/user/search", factory=default_factory)
    config.add_route("user_view", "/user/{username}", factory=user_factory)
    config.add_route("user_edit", "/user/{username}/edit", factory=user_factory)
    config.add_route("user_delete", "/user/{username}/delete", factory=user_factory)
    config.add_route(
        "user_companies", "/user/{username}/companies", factory=user_factory
    )
    config.add_route(
        "user_more_companies",
        "/user/{username}/more_companies",
        factory=user_factory,
    )
    config.add_route(
        "user_projects",
        "/user/{username}/projects",
        factory=user_factory,
    )
    config.add_route(
        "user_more_projects",
        "/user/{username}/more_projects",
        factory=user_factory,
    )
    config.add_route("user_tags", "/user/{username}/tags", factory=user_factory)
    config.add_route(
        "user_more_tags",
        "/user/{username}/more_tags",
        factory=user_factory,
    )
    config.add_route("user_contacts", "/user/{username}/contacts", factory=user_factory)
    config.add_route(
        "user_more_contacts",
        "/user/{username}/more_contacts",
        factory=user_factory,
    )
    config.add_route("user_comments", "/user/{username}/comments", factory=user_factory)
    config.add_route(
        "user_more_comments",
        "/user/{username}/more_comments",
        factory=user_factory,
    )
    config.add_route(
        "user_selected_companies",
        "/user/{username}/selected_companies",
        factory=user_factory,
    )
    config.add_route(
        "user_more_selected_companies",
        "/user/{username}/more_selected_companies",
        factory=user_factory,
    )
    config.add_route(
        "user_export_selected_companies",
        "/user/{username}/export_selected_companies",
        factory=user_factory,
    )
    config.add_route(
        "user_clear_selected_companies",
        "/user/{username}/clear_selected_companies",
        factory=user_factory,
    )
    config.add_route(
        "user_selected_projects",
        "/user/{username}/selected_projects",
        factory=user_factory,
    )
    config.add_route(
        "user_more_selected_projects",
        "/user/{username}/more_selected_projects",
        factory=user_factory,
    )
    config.add_route(
        "user_export_selected_projects",
        "/user/{username}/export_selected_projects",
        factory=user_factory,
    )
    config.add_route(
        "user_clear_selected_projects",
        "/user/{username}/clear_selected_projects",
        factory=user_factory,
    )
    config.add_route(
        "user_selected_tags",
        "/user/{username}/selected_tags",
        factory=user_factory,
    )
    config.add_route(
        "user_more_selected_tags",
        "/user/{username}/more_selected_tags",
        factory=user_factory,
    )
    config.add_route(
        "user_export_selected_tags",
        "/user/{username}/export_selected_tags",
        factory=user_factory,
    )
    config.add_route(
        "user_clear_selected_tags",
        "/user/{username}/clear_selected_tags",
        factory=user_factory,
    )
    config.add_route(
        "user_selected_contacts",
        "/user/{username}/selected_contacts",
        factory=user_factory,
    )
    config.add_route(
        "user_more_selected_contacts",
        "/user/{username}/more_selected_contacts",
        factory=user_factory,
    )
    config.add_route(
        "user_export_selected_contacts",
        "/user/{username}/export_selected_contacts",
        factory=user_factory,
    )
    config.add_route(
        "user_clear_selected_contacts",
        "/user/{username}/clear_selected_contacts",
        factory=user_factory,
    )
    config.add_route(
        "user_recommended", "/user/{username}/recommended", factory=user_factory
    )
    config.add_route(
        "user_more_recommended",
        "/user/{username}/more_recommended",
        factory=user_factory,
    )
    config.add_route(
        "user_export_recommended",
        "/user/{username}/export_recommended",
        factory=user_factory,
    )
    config.add_route(
        "user_clear_recommended",
        "/user/{username}/clear_recommended",
        factory=user_factory,
    )
    config.add_route("user_watched", "/user/{username}/watched", factory=user_factory)
    config.add_route(
        "user_more_watched",
        "/user/{username}/more_watched",
        factory=user_factory,
    )
    config.add_route(
        "user_export_watched",
        "/user/{username}/export_watched",
        factory=user_factory,
    )
    config.add_route(
        "user_clear_watched",
        "/user/{username}/clear_watched",
        factory=user_factory,
    )
