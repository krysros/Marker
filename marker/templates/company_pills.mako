<%! from marker.forms.ts import TranslationString as _ %>

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
%>

<%def name="pills(company)">
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