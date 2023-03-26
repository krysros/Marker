
<%def name="nav_company(company, active_link=None)">
  <ul class="nav nav-pills">
    <li class="nav-item">
    % if active_link == "company":
      <a class="nav-link active position-relative" aria-current="page" href="${request.route_url('company_view', company_id=company.id, slug=company.slug)}">Firma
        % if company.color != "default":
        <span class="position-absolute top-0 start-100 translate-middle p-2 bg-${company.color} border border-light rounded-circle">
          <span class="visually-hidden">Color</span>
        </span>
        % endif
      </a>
    % else:
      <a class="nav-link position-relative" href="${request.route_url('company_view', company_id=company.id, slug=company.slug)}">Firma</a>
    % endif
    </li>
    <li class="nav-item">
    % if active_link == "projects":
      <a class="nav-link active position-relative" aria-current="page" href="${request.route_url('company_projects', company_id=company.id, slug=company.slug)}">Projekty
        % if company.color != "default":
        <span class="position-absolute top-0 start-100 translate-middle p-2 bg-${company.color} border border-light rounded-circle">
          <span class="visually-hidden">Color</span>
        </span>
        % endif
        <span class="badge text-bg-secondary"><div hx-get="${request.route_url('company_count_projects', company_id=company.id, slug=company.slug)}" hx-trigger="projectCompanyEvent from:body">${company.count_projects}</div></span>
      </a>
    % else:
      <a class="nav-link" href="${request.route_url('company_projects', company_id=company.id, slug=company.slug)}">
        Projekty <span class="badge text-bg-secondary"><div hx-get="${request.route_url('company_count_projects', company_id=company.id, slug=company.slug)}" hx-trigger="projectCompanyEvent from:body">${company.count_projects}</div></span>
      </a>
    % endif
    </li>
    <li class="nav-item">
    % if active_link == "tags":
      <a class="nav-link active position-relative" aria-current="page" href="${request.route_url('company_tags', company_id=company.id, slug=company.slug)}">Tagi
        % if company.color != "default":
        <span class="position-absolute top-0 start-100 translate-middle p-2 bg-${company.color} border border-light rounded-circle">
          <span class="visually-hidden">Color</span>
        </span>
        % endif
        <span class="badge text-bg-secondary"><div hx-get="${request.route_url('company_count_tags', company_id=company.id, slug=company.slug)}" hx-trigger="tagEvent from:body">${company.count_tags}</div></span>
      </a>
    % else:
      <a class="nav-link" href="${request.route_url('company_tags', company_id=company.id, slug=company.slug)}">
        Tagi <span class="badge text-bg-secondary"><div hx-get="${request.route_url('company_count_tags', company_id=company.id, slug=company.slug)}" hx-trigger="tagEvent from:body">${company.count_tags}</div></span>
      </a>
    % endif
    </li>
    <li class="nav-item">
    % if active_link == "contacts":
      <a class="nav-link active position-relative" aria-current="page" href="${request.route_url('company_contacts', company_id=company.id, slug=company.slug)}">Kontakty
        % if company.color != "default":
        <span class="position-absolute top-0 start-100 translate-middle p-2 bg-${company.color} border border-light rounded-circle">
          <span class="visually-hidden">Color</span>
        </span>
        % endif
        <span class="badge text-bg-secondary"><div hx-get="${request.route_url('company_count_contacts', company_id=company.id, slug=company.slug)}" hx-trigger="contactEvent from:body">${company.count_contacts}</div></span>
      </a>
    % else:
      <a class="nav-link" href="${request.route_url('company_contacts', company_id=company.id, slug=company.slug)}">
        Kontakty <span class="badge text-bg-secondary"><div hx-get="${request.route_url('company_count_contacts', company_id=company.id, slug=company.slug)}" hx-trigger="contactEvent from:body">${company.count_contacts}</div></span>
      </a>
    % endif
    </li>
    <li class="nav-item">
    % if active_link == "comments":
      <a class="nav-link active position-relative" aria-current="page" href="${request.route_url('company_comments', company_id=company.id, slug=company.slug)}">Komentarze
        % if company.color != "default":
        <span class="position-absolute top-0 start-100 translate-middle p-2 bg-${company.color} border border-light rounded-circle">
          <span class="visually-hidden">Color</span>
        </span>
        % endif
        <span class="badge text-bg-secondary"><div hx-get="${request.route_url('company_count_comments', company_id=company.id, slug=company.slug)}" hx-trigger="commentEvent from:body">${company.count_comments}</div></span>
      </a>
    % else:
      <a class="nav-link" href="${request.route_url('company_comments', company_id=company.id, slug=company.slug)}">
        Komentarze <span class="badge text-bg-secondary"><div hx-get="${request.route_url('company_count_comments', company_id=company.id, slug=company.slug)}" hx-trigger="commentEvent from:body">${company.count_comments}</div></span>
      </a>
    % endif
    </li>
    <li class="nav-item">
    % if active_link == "recommended":
      <a class="nav-link active position-relative" aria-current="page" href="${request.route_url('company_recommended', company_id=company.id, slug=company.slug)}">Rekomendacje
        % if company.color != "default":
        <span class="position-absolute top-0 start-100 translate-middle p-2 bg-${company.color} border border-light rounded-circle">
          <span class="visually-hidden">Color</span>
        </span>
        % endif
        <span class="badge text-bg-secondary"><div hx-get="${request.route_url('company_count_recommended', company_id=company.id, slug=company.slug)}" hx-trigger="recommendEvent from:body">${company.count_recommended}</div></span>
      </a>
    % else:
      <a class="nav-link" href="${request.route_url('company_recommended', company_id=company.id, slug=company.slug)}">
        Rekomendacje <span class="badge text-bg-secondary"><div hx-get="${request.route_url('company_count_recommended', company_id=company.id, slug=company.slug)}" hx-trigger="recommendEvent from:body">${company.count_recommended}</div></span>
      </a>
    % endif
    </li>
    <li class="nav-item">
    % if active_link == "similar":
      <a class="nav-link active position-relative" aria-current="page" href="${request.route_url('company_similar', company_id=company.id, slug=company.slug)}">Podobne
        % if company.color != "default":
        <span class="position-absolute top-0 start-100 translate-middle p-2 bg-${company.color} border border-light rounded-circle">
          <span class="visually-hidden">Color</span>
        </span>
        % endif
        <span class="badge text-bg-secondary"><div id="similar-companies" hx-get="${request.route_url('company_count_similar', company_id=company.id, slug=company.slug)}" hx-trigger="tagEvent from:body">${company.count_similar}</div></span>
      </a>
    % else:
      <a class="nav-link" href="${request.route_url('company_similar', company_id=company.id, slug=company.slug)}">
        Podobne <span class="badge text-bg-secondary"><div id="similar-companies" hx-get="${request.route_url('company_count_similar', company_id=company.id, slug=company.slug)}" hx-trigger="tagEvent from:body">${company.count_similar}</div></span>
      </a>
    % endif
    </li>
  </ul>
</%def>


<%def name="nav_project(project, active_link=None)">
  <ul class="nav nav-pills">
    <li class="nav-item">
    % if active_link == "project":
      <a class="nav-link active position-relative" aria-current="page" href="${request.route_url('project_view', project_id=project.id, slug=project.slug)}">Projekt
        % if project.color != "default":
        <span class="position-absolute top-0 start-100 translate-middle p-2 bg-${project.color} border border-light rounded-circle">
          <span class="visually-hidden">Color</span>
        </span>
        % endif
      </a>
    % else:
      <a class="nav-link position-relative" href="${request.route_url('project_view', project_id=project.id, slug=project.slug)}">Projekt</a>
    % endif
    </li>
    <li class="nav-item">
    % if active_link == "companies":
      <a class="nav-link active position-relative" aria-current="page" href="${request.route_url('project_companies', project_id=project.id, slug=project.slug)}">Firmy
        % if project.color != "default":
        <span class="position-absolute top-0 start-100 translate-middle p-2 bg-${project.color} border border-light rounded-circle">
          <span class="visually-hidden">Color</span>
        </span>
        % endif
        <span class="badge text-bg-secondary"><div hx-get="${request.route_url('project_count_companies', project_id=project.id, slug=project.slug)}" hx-trigger="projectCompanyEvent from:body">${project.count_companies}</div></span>
      </a>
    % else:
      <a class="nav-link" href="${request.route_url('project_companies', project_id=project.id, slug=project.slug)}">
        Firmy <span class="badge text-bg-secondary"><div hx-get="${request.route_url('project_count_companies', project_id=project.id, slug=project.slug)}" hx-trigger="projectCompanyEvent from:body">${project.count_companies}</div></span>
      </a>
    % endif
    </li>
    <li class="nav-item">
    % if active_link == "tags":
      <a class="nav-link active position-relative" aria-current="page" href="${request.route_url('project_tags', project_id=project.id, slug=project.slug)}">Tagi
        % if project.color != "default":
        <span class="position-absolute top-0 start-100 translate-middle p-2 bg-${project.color} border border-light rounded-circle">
          <span class="visually-hidden">Color</span>
        </span>
        % endif
        <span class="badge text-bg-secondary"><div hx-get="${request.route_url('project_count_tags', project_id=project.id, slug=project.slug)}" hx-trigger="tagEvent from:body">${project.count_tags}</div></span>
      </a>
    % else:
      <a class="nav-link" href="${request.route_url('project_tags', project_id=project.id, slug=project.slug)}">
        Tagi <span class="badge text-bg-secondary"><div hx-get="${request.route_url('project_count_tags', project_id=project.id, slug=project.slug)}" hx-trigger="tagEvent from:body">${project.count_tags}</div></span>
      </a>
    % endif
    </li>
    <li class="nav-item">
    % if active_link == "contacts":
      <a class="nav-link active position-relative" aria-current="page" href="${request.route_url('project_contacts', project_id=project.id, slug=project.slug)}">Kontakty
        % if project.color != "default":
        <span class="position-absolute top-0 start-100 translate-middle p-2 bg-${project.color} border border-light rounded-circle">
          <span class="visually-hidden">Color</span>
        </span>
        % endif
        <span class="badge text-bg-secondary"><div hx-get="${request.route_url('project_count_contacts', project_id=project.id, slug=project.slug)}" hx-trigger="contactEvent from:body">${project.count_contacts}</div></span>
      </a>
    % else:
      <a class="nav-link" href="${request.route_url('project_contacts', project_id=project.id, slug=project.slug)}">
        Kontakty <span class="badge text-bg-secondary"><div hx-get="${request.route_url('project_count_contacts', project_id=project.id, slug=project.slug)}" hx-trigger="contactEvent from:body">${project.count_contacts}</div></span>
      </a>
    % endif
    </li>
    <li class="nav-item">
    % if active_link == "comments":
      <a class="nav-link active position-relative" aria-current="page" href="${request.route_url('project_comments', project_id=project.id, slug=project.slug)}">Komentarze
        % if project.color != "default":
        <span class="position-absolute top-0 start-100 translate-middle p-2 bg-${project.color} border border-light rounded-circle">
          <span class="visually-hidden">Color</span>
        </span>
        % endif
        <span class="badge text-bg-secondary"><div hx-get="${request.route_url('project_count_comments', project_id=project.id, slug=project.slug)}" hx-trigger="commentEvent from:body">${project.count_comments}</div></span>
      </a>
    % else:
      <a class="nav-link" href="${request.route_url('project_comments', project_id=project.id, slug=project.slug)}">
        Komentarze <span class="badge text-bg-secondary"><div hx-get="${request.route_url('project_count_comments', project_id=project.id, slug=project.slug)}" hx-trigger="commentEvent from:body">${project.count_comments}</div></span>
      </a>
    % endif
    </li>
    <li class="nav-item">
    % if active_link == "watched":
      <a class="nav-link active position-relative" aria-current="page" href="${request.route_url('project_watched', project_id=project.id, slug=project.slug)}">Obserwacje
        % if project.color != "default":
        <span class="position-absolute top-0 start-100 translate-middle p-2 bg-${project.color} border border-light rounded-circle">
          <span class="visually-hidden">Color</span>
        </span>
        % endif
        <span class="badge text-bg-secondary"><div hx-get="${request.route_url('project_count_watched', project_id=project.id, slug=project.slug)}" hx-trigger="recommendEvent from:body">${project.count_watched}</div></span>
      </a>
    % else:
      <a class="nav-link" href="${request.route_url('project_watched', project_id=project.id, slug=project.slug)}">
        Obserwacje <span class="badge text-bg-secondary"><div hx-get="${request.route_url('project_count_watched', project_id=project.id, slug=project.slug)}" hx-trigger="recommendEvent from:body">${project.count_watched}</div></span>
      </a>
    % endif
    </li>
    <li class="nav-item">
    % if active_link == "similar":
      <a class="nav-link active position-relative" aria-current="page" href="${request.route_url('project_similar', project_id=project.id, slug=project.slug)}">Podobne
        % if project.color != "default":
        <span class="position-absolute top-0 start-100 translate-middle p-2 bg-${project.color} border border-light rounded-circle">
          <span class="visually-hidden">Color</span>
        </span>
        % endif
        <span class="badge text-bg-secondary"><div id="similar-companies" hx-get="${request.route_url('project_count_similar', project_id=project.id, slug=project.slug)}" hx-trigger="tagEvent from:body">${project.count_similar}</div></span>
      </a>
    % else:
      <a class="nav-link" href="${request.route_url('project_similar', project_id=project.id, slug=project.slug)}">
        Podobne <span class="badge text-bg-secondary"><div id="similar-companies" hx-get="${request.route_url('project_count_similar', project_id=project.id, slug=project.slug)}" hx-trigger="tagEvent from:body">${project.count_similar}</div></span>
      </a>
    % endif
    </li>
  </ul>
</%def>