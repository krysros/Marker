<%! from marker.forms.ts import TranslationString as _ %>

<%def name="pills(project)">
  <%
  project_pills = [
    {"title": _("Project"), "route_name": "project_view", "event": "projectCompanyEvent"},
    {"title": _("Companies"), "route_name": "project_companies", "event": "projectCompanyEvent"},
    {"title": _("Tags"), "route_name": "project_tags", "event": "tagEvent"},
    {"title": _("Contacts"), "route_name": "project_contacts", "event": "contactEvent"},
    {"title": _("Companies"), "route_name": "project_comments", "event": "commentEvent"},
    {"title": _("Watched"), "route_name": "project_watched", "event": "watchEvent"},
    {"title": _("Similar"), "route_name": "project_similar", "event": "tagEvent"},
  ]
  %>
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