<%page args="theme"/>
<nav class="navbar navbar-expand-md fixed-top bg-${theme}">
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
              <a class="dropdown-item" role="button" hx-get="${request.route_url('theme')}" hx-swap="none">
              % if theme == "dark":
                <i class="bi bi-sun"></i> ${_("Light")}
              % else:
                <i class="bi bi-moon"></i> ${_("Dark")}
              % endif
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
      </ul>
    </div>
  </div>
</nav>