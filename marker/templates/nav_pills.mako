<%!

  company_pills = [
    {"title": "Firma", "route_name": "company_view"},
    {"title": "Projekty", "route_name": "company_projects"},
    {"title": "Tagi", "route_name": "company_tags"},
    {"title": "Kontakty", "route_name": "company_contacts"},
    {"title": "Komentarze", "route_name": "company_comments"},
    {"title": "Rekomendacje", "route_name": "company_recommended"},
    {"title": "Podobne", "route_name": "company_similar"},
  ]

  project_pills = [
    {"title": "Projekt", "route_name": "project_view"},
    {"title": "Firmy", "route_name": "project_companies"},
    {"title": "Tagi", "route_name": "project_tags"},
    {"title": "Kontakty", "route_name": "project_contacts"},
    {"title": "Komentarze", "route_name": "project_comments"},
    {"title": "Obserwacje", "route_name": "project_watched"},
    {"title": "Podobne", "route_name": "project_similar"},
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
                 hx-trigger="projectCompanyEvent from:body">
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
                 hx-trigger="projectCompanyEvent from:body">
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
                 hx-trigger="projectprojectEvent from:body">
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
                 hx-trigger="projectprojectEvent from:body">
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