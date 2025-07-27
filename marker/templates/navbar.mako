<nav class="navbar navbar-expand-md fixed-top bg-body-tertiary">
  <div class="container-fluid">
    <a class="navbar-brand" href="${request.route_url('home')}">Marker</a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarNav">
      <ul class="navbar-nav me-auto mb-2 mb-md-0">
        <li class="nav-item">
          <a class="nav-link" role="button" href="${request.route_url('company_all')}"><i class="bi bi-buildings"></i> ${_("Companies")}</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" role="button" href="${request.route_url('project_all')}"><i class="bi bi-briefcase"></i> ${_("Projects")}</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" role="button" href="${request.route_url('tag_all')}"><i class="bi bi-tags"></i> ${_("Tags")}</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" role="button" href="${request.route_url('contact_all')}"><i class="bi bi-people"></i> ${_("Contacts")}</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" role="button" href="${request.route_url('comment_all')}"><i class="bi bi-chat-left-text"></i> ${_("Comments")}</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" role="button" href="${request.route_url('report')}"><i class="bi bi-bar-chart"></i> ${_("Reports")}</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" role="button" href="${request.route_url('user_all')}"><i class="bi bi-person-circle"></i> ${_("Users")}</a>
        </li>
      </ul>
      <ul class="navbar-nav ms-auto">
        % if not request.is_authenticated:
        <li class="nav-item">
          <a class="nav-link" role="button" href="${request.application_url}/login">${_("Log in")}</a>
        </li>
        % else:
        <li class="nav-item dropdown">
          <a class="nav-link dropdown-toggle" role="button" id="dropdown-account" data-bs-toggle="dropdown" aria-expanded="false">
            <i class="bi bi-gear"></i> ${request.identity.name}
          </a>
          <ul class="dropdown-menu dropdown-menu-end">
            <li><h6 class="dropdown-header">${_("Selected")}</h6></li>
            <li>
              <a class="dropdown-item" role="button" href="${request.route_url('user_selected_companies', username=request.identity.name)}">
                <i class="bi bi-buildings"></i> ${_("Companies")}
              </a>
            </li>
            <li>
              <a class="dropdown-item" role="button" href="${request.route_url('user_selected_projects', username=request.identity.name)}">
                <i class="bi bi-briefcase"></i> ${_("Projects")}
              </a>
            </li>
            <li>
              <a class="dropdown-item" role="button" href="${request.route_url('user_selected_tags', username=request.identity.name)}">
                <i class="bi bi-tags"></i> ${_("Tags")}
              </a>
            </li>
            <li>
              <a class="dropdown-item" role="button" href="${request.route_url('user_selected_contacts', username=request.identity.name)}">
                <i class="bi bi-people"></i> ${_("Contacts")}
              </a>
            </li>
            <li><h6 class="dropdown-header">${_("Stars")}</h6></li>
            <li>
              <a class="dropdown-item" role="button" href="${request.route_url('user_companies_stars', username=request.identity.name)}">
                <i class="bi bi-buildings"></i> ${_("Companies")}
              </a>
            </li>
            <li>
              <a class="dropdown-item" role="button" href="${request.route_url('user_projects_stars', username=request.identity.name)}">
                <i class="bi bi-briefcase"></i> ${_("Projects")}
              </a>
            </li>
            <li><hr class="dropdown-divider"></li>
            <li>
              <a class="dropdown-item" role="button" href="${request.route_url('account', username=request.identity.name)}">
                ${_("Account")}
              </a>
            </li>
            <li><hr class="dropdown-divider"></li>
            <li>
              <form action="${request.route_url('logout')}" method="post">
                <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
                <button type="submit" class="dropdown-item">${_("Log out")}</button>
              </form>
            </li>
          </ul>
        </li>
        % endif
        <li class="nav-item dropdown">
          <a class="nav-link dropdown-toggle" href="#" id="themeDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
            <output id="theme-icon"><i class="bi bi-circle-half"></i></output>
          </a>
          <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="themeDropdown">
            <li>
              <a class="dropdown-item d-flex align-items-center" href="#" data-bs-theme-value="light" hx-post="${request.route_url('theme', theme='light')}" hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}' hx-swap="innerHTML" hx-target="#theme-icon">
                <i class="bi bi-sun-fill me-2"></i> ${_("Light")}
              </a>
            </li>
            <li>
              <a class="dropdown-item d-flex align-items-center" href="#" data-bs-theme-value="dark" hx-post="${request.route_url('theme', theme='dark')}" hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}' hx-swap="innerHTML" hx-target="#theme-icon">
                <i class="bi bi-moon-stars-fill me-2"></i> ${_("Dark")}
              </a>
            </li>
            <li>
              <a class="dropdown-item d-flex align-items-center" href="#" data-bs-theme-value="auto" hx-post="${request.route_url('theme', theme='auto')}" hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}' hx-swap="innerHTML" hx-target="#theme-icon">
                <i class="bi bi-circle-half me-2"></i> ${_("Auto")}
              </a>
            </li>
          </ul>
        </li>
      </ul>
    </div>
  </div>
</nav>