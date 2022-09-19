<nav class="navbar navbar-expand-md fixed-top bg-light">
  <div class="container-fluid">
    <a class="navbar-brand" href="#" hx-get="${request.route_url('home')}" hx-target="#main-container" hx-swap="innerHTML show:window:top">Marker</a>
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
      <%include file="menu.mako"/>
    </div>
  </div>
</nav>