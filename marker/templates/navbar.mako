<nav class="navbar navbar-expand-md fixed-top bg-light">
  <div class="container-fluid">
    <a class="navbar-brand" href="${request.route_url('home')}">Marker</a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarNav">
      <ul class="navbar-nav me-auto mb-2 mb-md-0">
        <li class="nav-item">
          <a class="nav-link" role="button" href="#" hx-get="${request.route_url('company_all')}" hx-target="#main-container" hx-swap="innerHTML show:window:top"><i class="bi bi-building"></i> Firmy</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" role="button" href="#" hx-get="${request.route_url('project_all')}" hx-target="#main-container" hx-swap="innerHTML show:window:top"><i class="bi bi-briefcase"></i> Projekty</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" role="button" href="#" hx-get="${request.route_url('tag_all')}" hx-target="#main-container" hx-swap="innerHTML show:window:top"><i class="bi bi-tags"></i> Tagi</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" role="button" href="#" hx-get="${request.route_url('person_all')}" hx-target="#main-container" hx-swap="innerHTML show:window:top"><i class="bi bi-people"></i> Osoby</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" role="button" href="#" hx-get="${request.route_url('user_all')}" hx-target="#main-container" hx-swap="innerHTML show:window:top"><i class="bi bi-person-circle"></i> Użytkownicy</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" role="button" href="#" hx-get="${request.route_url('comment_all')}" hx-target="#main-container" hx-swap="innerHTML show:window:top"><i class="bi bi-chat-left-text"></i> Komentarze</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" role="button" href="#" hx-get="${request.route_url('report')}" hx-target="#main-container" hx-swap="innerHTML show:window:top"><i class="bi bi-bar-chart"></i> Raporty</a>
        </li>
      </ul>
      <ul class="navbar-nav ms-auto">
        % if not request.is_authenticated:
        <li class="nav-item">
          <a class="nav-link" role="button" hx-get="${request.application_url}/login" hx-target="#main-container">Zaloguj</a>
        </li>
        % else:
        <li class="nav-item dropdown">
          <a class="nav-link dropdown-toggle" href="#" role="button" id="dropdown-account" data-bs-toggle="dropdown" aria-expanded="false">
            <i class="bi bi-gear"></i> ${request.identity.name}
          </a>
          <ul class="dropdown-menu dropdown-menu-end">
            <li>
              <a class="dropdown-item" role="button" href="#" hx-get="${request.route_url('user_checked', username=request.identity.name)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">
                <i class="bi bi-check-square"></i> Zaznaczone
              </a>
            </li>
            <li>
              <a class="dropdown-item" role="button" href="#" hx-get="${request.route_url('user_recomended', username=request.identity.name)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">
                <i class="bi bi-hand-thumbs-up"></i> Rekomendowane
              </a>
            </li>
            <li>
              <a class="dropdown-item" role="button" href="#" hx-get="${request.route_url('user_watched', username=request.identity.name)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">
                <i class="bi bi-eye"></i> Obserwowane
              </a>
            </li>
            <li><hr class="dropdown-divider"></li>
            <li>
              <a class="dropdown-item" role="button" href="#" hx-get="${request.route_url('account', username=request.identity.name)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">
                Konto
              </a>
            </li>
            <li><hr class="dropdown-divider"></li>
            <li>
              <a class="dropdown-item" hx-post="${request.route_url('logout')}" hx-target="#main-container" hx-role="button">
                Wyloguj
              </a>
            </li>
          </ul>
        </li>
        % endif
      </ul>
    </div>
  </div>
</nav>