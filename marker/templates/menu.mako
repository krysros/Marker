<ul class="navbar-nav ms-auto">
  % if not request.is_authenticated:
  <li class="nav-item">
    <a class="nav-link" role="button" hx-get="${request.application_url}/login" hx-target="#main-container" hx-swap="innerHTML show:window:top">Zaloguj</a>
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
        <form hx-post="${request.route_url('logout')}" hx-target="#main-container" hx-swap="innerHTML show:window:top">
          <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
          <button type="submit" class="dropdown-item">Wyloguj</button>
        </form>
      </li>
    </ul>
  </li>
  % endif
</ul>