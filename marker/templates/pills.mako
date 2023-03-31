<%!

  company_pills = [
    {"title": _("Company"), "route_name": "company_view", "event": "projectCompanyEvent"},
    {"title": _("Projects"), "route_name": "company_projects", "event": "projectCompanyEvent"},
    {"title": _("Tags"), "route_name": "company_tags", "event": "tagEvent"},
    {"title": _("Contacts"), "route_name": "company_contacts", "event": "contactEvent"},
    {"title": _("Comments"), "route_name": "company_comments", "event": "commentEvent"},
    {"title": _("Recommended"), "route_name": "company_recommended", "event": "recommendEvent"},
    {"title": _("Similar"), "route_name": "company_similar", "event": "tagEvent"},
  ]

  project_pills = [
    {"title": _("Project"), "route_name": "project_view", "event": "projectCompanyEvent"},
    {"title": _("Companies"), "route_name": "project_companies", "event": "projectCompanyEvent"},
    {"title": _("Tags"), "route_name": "project_tags", "event": "tagEvent"},
    {"title": _("Contacts"), "route_name": "project_contacts", "event": "contactEvent"},
    {"title": _("Companies"), "route_name": "project_comments", "event": "commentEvent"},
    {"title": _("Watched"), "route_name": "project_watched", "event": "watchEvent"},
    {"title": _("Similar"), "route_name": "project_similar", "event": "tagEvent"},
  ]

  tag_pills = [
    {"title": _("Tag"), "route_name": "tag_view", "event": "tagEvent"},
    {"title": _("Companies"), "route_name": "tag_companies", "event": "tagEvent"},
    {"title": _("Projects"), "route_name": "tag_projects", "event": "tagEvent"},
  ]

  user_pills = [
    {"title": _("User"), "route_name": "user_view"},
    {"title": _("Companies"), "route_name": "user_companies"},
    {"title": _("Projects"), "route_name": "user_projects"},
    {"title": _("Tags"), "route_name": "user_tags"},
    {"title": _("Contacts"), "route_name": "user_contacts"},
    {"title": _("Comments"), "route_name": "user_comments"},
  ]

%>


<%def name="company_pill(company)">
  <ul class="nav nav-pills">
  % for pill in company_pills:
    <li class="nav-item">
    % if request.matched_route.name == pill["route_name"]:
      <a class="nav-link active position-relative" aria-current="page" href="${request.route_url(pill['route_name'], company_id=company.id, slug=company.slug)}">
        ${pill["title"]}
        % if company.color != "default":
          <span class="position-absolute top-0 start-100 translate-middle p-2 bg-${company.color} border border-light rounded-circle">
            <span class="visually-hidden">Color</span>
          </span>
        % endif
        % if not pill["route_name"].endswith("_view"):
          <span class="badge text-bg-secondary">
            <div hx-get="${request.route_url('_count_'.join(pill['route_name'].split('_')), company_id=company.id, slug=company.slug)}"
                 hx-trigger="${pill['event']} from:body">
              ${getattr(company, pill["route_name"].replace("company_", "count_"))}
            </div>
          </span>
        % endif
      </a>
    % else:
      <a class="nav-link" href="${request.route_url(pill['route_name'], company_id=company.id, slug=company.slug)}">
        ${pill["title"]}
        % if not pill["route_name"].endswith("_view"):
          <span class="badge text-bg-secondary">
            <div hx-get="${request.route_url('_count_'.join(pill['route_name'].split('_')), company_id=company.id, slug=company.slug)}"
                 hx-trigger="${pill['event']} from:body">
              ${getattr(company, pill["route_name"].replace("company_", "count_"))}
            </div>
          </span>
        % endif
      </a>
    % endif
    </li>
  % endfor
  </ul>
</%def>


<%def name="project_pill(project)">
  <ul class="nav nav-pills">
  % for pill in project_pills:
    <li class="nav-item">
    % if request.matched_route.name == pill["route_name"]:
      <a class="nav-link active position-relative" aria-current="page" href="${request.route_url(pill['route_name'], project_id=project.id, slug=project.slug)}">
        ${pill["title"]}
        % if project.color != "default":
          <span class="position-absolute top-0 start-100 translate-middle p-2 bg-${project.color} border border-light rounded-circle">
            <span class="visually-hidden">Color</span>
          </span>
        % endif
        % if not pill["route_name"].endswith("_view"):
          <span class="badge text-bg-secondary">
            <div hx-get="${request.route_url('_count_'.join(pill['route_name'].split('_')), project_id=project.id, slug=project.slug)}"
                 hx-trigger="${pill['event']} from:body">
              ${getattr(project, pill["route_name"].replace("project_", "count_"))}
            </div>
          </span>
        % endif
      </a>
    % else:
      <a class="nav-link" href="${request.route_url(pill['route_name'], project_id=project.id, slug=project.slug)}">
        ${pill["title"]}
        % if not pill["route_name"].endswith("_view"):
          <span class="badge text-bg-secondary">
            <div hx-get="${request.route_url('_count_'.join(pill['route_name'].split('_')), project_id=project.id, slug=project.slug)}"
                 hx-trigger="${pill['event']} from:body">
              ${getattr(project, pill["route_name"].replace("project_", "count_"))}
            </div>
          </span>
        % endif
      </a>
    % endif
    </li>
  % endfor
  </ul>
</%def>


<%def name="tag_pill(tag)">
  <ul class="nav nav-pills">
  % for pill in tag_pills:
    <li class="nav-item">
    % if request.matched_route.name == pill["route_name"] or request.matched_route.name == '_map_'.join(pill['route_name'].split('_')):
      <a class="nav-link active position-relative" aria-current="page" href="${request.route_url(pill['route_name'], tag_id=tag.id, slug=tag.slug)}">
        ${pill["title"]}
        % if not pill["route_name"].endswith("_view"):
          <span class="badge text-bg-secondary">
            <div hx-get="${request.route_url('_count_'.join(pill['route_name'].split('_')), tag_id=tag.id, slug=tag.slug)}"
                 hx-trigger="${pill['event']} from:body">
              ${getattr(tag, pill["route_name"].replace("tag_", "count_"))}
            </div>
          </span>
        % endif
      </a>
    % else:
      <a class="nav-link" href="${request.route_url(pill['route_name'], tag_id=tag.id, slug=tag.slug)}">
        ${pill["title"]}
        % if not pill["route_name"].endswith("_view"):
          <span class="badge text-bg-secondary">
            <div hx-get="${request.route_url('_count_'.join(pill['route_name'].split('_')), tag_id=tag.id, slug=tag.slug)}"
                 hx-trigger="${pill['event']} from:body">
              ${getattr(tag, pill["route_name"].replace("tag_", "count_"))}
            </div>
          </span>
        % endif
      </a>
    % endif
    </li>
  % endfor
  </ul>
</%def>


<%def name="user_pill(user)">
  <ul class="nav nav-pills">
  % for pill in user_pills:
    <li class="nav-item">
    % if request.matched_route.name == pill["route_name"] or request.matched_route.name == '_map_'.join(pill['route_name'].split('_')):
      <a class="nav-link active" aria-current="page" href="${request.route_url(pill['route_name'], username=user.name)}">
        ${pill["title"]}
        % if not pill["route_name"].endswith("_view"):
          <span class="badge text-bg-secondary">
            ${getattr(user, pill["route_name"].replace("user_", "count_"))}
          </span>
        % endif
      </a>
    % else:
      <a class="nav-link" href="${request.route_url(pill['route_name'], username=user.name)}">
        ${pill["title"]}
        % if not pill["route_name"].endswith("_view"):
          <span class="badge text-bg-secondary">
            ${getattr(user, pill["route_name"].replace("user_", "count_"))}
          </span>
        % endif
      </a>
    % endif
    </li>
  % endfor
  </ul>
</%def>