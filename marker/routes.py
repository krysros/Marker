from marker.factories import (
    default_factory,
    account_factory,
    branch_factory,
    company_factory,
    comment_factory,
    person_factory,
    investment_factory,
    user_factory,
    document_factory,
)


def includeme(config):
    config.add_static_view("static", "static", cache_max_age=3600)
    config.add_static_view("static_deform", "deform:static")
    config.add_route("home", "/")
    config.add_route("login", "/login")
    config.add_route("logout", "/logout")

    config.add_route("account", "/account", factory=account_factory)
    config.add_route("password", "/password", factory=account_factory)

    config.add_route("report", "/report", factory=default_factory)
    config.add_route(
        "report_results", "/report/{rel}", factory=default_factory
    )
    config.add_route(
        "report_more", "/report/{rel}/more", factory=default_factory
    )

    config.add_route("branch_all", "/branch", factory=default_factory)
    config.add_route("branch_more", "/branch/more", factory=default_factory)
    config.add_route(
        "branch_view",
        r"/branch/{branch_id:\d+}/{slug}/companies",
        factory=branch_factory,
    )
    config.add_route(
        "branch_view_more",
        r"/branch/{branch_id:\d+}/{slug}/companies/more",
        factory=branch_factory,
    )
    config.add_route(
        "branch_export",
        r"/branch/{branch_id:\d+}/export",
        factory=branch_factory,
    )
    config.add_route("branch_add", "/branch/add", factory=default_factory)
    config.add_route(
        "branch_search", "/branch/search", factory=default_factory
    )
    config.add_route(
        "branch_results", "/branch/results", factory=default_factory
    )
    config.add_route(
        "branch_results_more", "/branch/results/more", factory=default_factory
    )
    config.add_route(
        "branch_select", "/branch/select", factory=default_factory
    )
    config.add_route(
        "branch_edit",
        r"/branch/{branch_id:\d+}/{slug}/edit",
        factory=branch_factory,
    )
    config.add_route(
        "branch_delete",
        r"/branch/{branch_id:\d+}/{slug}/delete",
        factory=branch_factory,
    )

    config.add_route("company_all", "/company", factory=default_factory)
    config.add_route("company_more", "/company/more", factory=default_factory)
    config.add_route("company_add", "/company/add", factory=default_factory)
    config.add_route(
        "company_search", "/company/search", factory=default_factory
    )
    config.add_route(
        "company_results", "/company/results", factory=default_factory
    )
    config.add_route(
        "company_results_more",
        "/company/results/more",
        factory=default_factory,
    )
    config.add_route(
        "company_select", "/company/select", factory=default_factory
    )
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
        "company_investments",
        r"/company/{company_id:\d+}/{slug}/investments",
        factory=company_factory,
    )
    config.add_route(
        "company_investments_more",
        r"/company/{company_id:\d+}/{slug}/investments/more",
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
        "company_upvotes",
        r"/company/{company_id:\d+}/{slug}/upvotes",
        factory=company_factory,
    )
    config.add_route(
        "company_upvotes_more",
        r"/company/{company_id:\d+}/{slug}/upvotes/more",
        factory=company_factory,
    )
    config.add_route(
        "company_upvote",
        r"/upvote/company/{company_id:\d+}",
        factory=company_factory,
    )
    config.add_route(
        "company_mark",
        r"/mark/company/{company_id:\d+}",
        factory=company_factory,
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
    config.add_route(
        "comment_search", "/comment/search", factory=default_factory
    )
    config.add_route(
        "comment_results", "/comment/results", factory=default_factory
    )
    config.add_route(
        "comment_results_more",
        "/comment/results/more",
        factory=default_factory,
    )

    config.add_route(
        "contract",
        r"/company/{company_id:\d+}/{slug}/contract",
        factory=company_factory,
    )
    config.add_route(
        "envelope",
        r"/company/{company_id:\d+}/{slug}/envelope",
        factory=company_factory,
    )

    config.add_route(
        "person_vcard",
        r"/person/{person_id:\d+}/vcard",
        factory=person_factory,
    )
    config.add_route(
        "person_search", "/person/search", factory=default_factory
    )
    config.add_route(
        "person_results", "/person/results", factory=default_factory
    )
    config.add_route(
        "person_results_more", "/person/results/more", factory=default_factory
    )

    config.add_route("investment_all", "/investment", factory=default_factory)
    config.add_route(
        "investment_more", "/investment/more", factory=default_factory
    )
    config.add_route(
        "investment_add", "/investment/add", factory=default_factory
    )
    config.add_route(
        "investment_search", "/investment/search", factory=default_factory
    )
    config.add_route(
        "investment_results", "/investment/results", factory=default_factory
    )
    config.add_route(
        "investment_results_more",
        "/investment/results/more",
        factory=default_factory,
    )
    config.add_route(
        "investment_select", "/investment/select", factory=default_factory
    )
    config.add_route(
        "investment_export", r"/investments/export", factory=default_factory
    )
    config.add_route(
        "investment_view",
        r"/investment/{investment_id:\d+}/{slug}",
        factory=investment_factory,
    )
    config.add_route(
        "investment_edit",
        r"/investment/{investment_id:\d+}/{slug}/edit",
        factory=investment_factory,
    )
    config.add_route(
        "investment_delete",
        r"/investment/{investment_id:\d+}/{slug}/delete",
        factory=investment_factory,
    )
    config.add_route(
        "investment_follow",
        r"/follow/investment/{investment_id:\d+}",
        factory=investment_factory,
    )

    config.add_route("user_all", "/user", factory=default_factory)
    config.add_route("user_more", "/user/more", factory=default_factory)
    config.add_route("user_add", "/user/add", factory=default_factory)
    config.add_route("user_search", "/user/search", factory=default_factory)
    config.add_route("user_results", "/user/results", factory=default_factory)
    config.add_route(
        "user_results_more", "/user/results/more", factory=default_factory
    )
    config.add_route("user_view", "/user/{username}", factory=user_factory)
    config.add_route(
        "user_edit", "/user/{username}/edit", factory=user_factory
    )
    config.add_route(
        "user_delete", "/user/{username}/delete", factory=user_factory
    )
    config.add_route(
        "user_comments", "/user/{username}/comments", factory=user_factory
    )
    config.add_route(
        "user_comments_more",
        "/user/{username}/comments/more",
        factory=user_factory,
    )
    config.add_route(
        "user_branches", "/user/{username}/branches", factory=user_factory
    )
    config.add_route(
        "user_branches_more",
        "/user/{username}/branches/more",
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
        "user_investments",
        "/user/{username}/investments",
        factory=user_factory,
    )
    config.add_route(
        "user_investments_more",
        "/user/{username}/investments/more",
        factory=user_factory,
    )
    config.add_route(
        "user_marked", "/user/{username}/marked", factory=user_factory
    )
    config.add_route(
        "user_marked_more",
        "/user/{username}/marked/more",
        factory=user_factory,
    )
    config.add_route(
        "user_marked_export",
        "/user/{username}/marked/export",
        factory=user_factory,
    )
    config.add_route(
        "user_marked_clear",
        "/user/{username}/marked/clear",
        factory=user_factory,
    )
    config.add_route(
        "user_upvotes", "/user/{username}/upvotes", factory=user_factory
    )
    config.add_route(
        "user_upvotes_more",
        "/user/{username}/upvotes/more",
        factory=user_factory,
    )
    config.add_route(
        "user_upvotes_export",
        "/user/{username}/upvotes/export",
        factory=user_factory,
    )
    config.add_route(
        "user_upvotes_clear",
        "/user/{username}/upvotes/clear",
        factory=user_factory,
    )
    config.add_route(
        "user_following", "/user/{username}/following", factory=user_factory
    )
    config.add_route(
        "user_following_more",
        "/user/{username}/following/more",
        factory=user_factory,
    )
    config.add_route(
        "user_following_export",
        "/user/{username}/following/export",
        factory=user_factory,
    )
    config.add_route(
        "user_following_clear",
        "/user/{username}/following/clear",
        factory=user_factory,
    )

    config.add_route("document_all", "/document", factory=default_factory)
    config.add_route(
        "document_more", "/document/more", factory=default_factory
    )
    config.add_route(
        "document_upload", "/document/upload", factory=default_factory
    )
    config.add_route(
        "document_download",
        r"/document/{document_id:\d+}/download",
        factory=document_factory,
    )
    config.add_route(
        "document_delete",
        r"/document/{document_id:\d+}/delete",
        factory=document_factory,
    )
