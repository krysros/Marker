<!DOCTYPE html>
<html lang="${request.locale_name}">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="Informacje o firmach i projektach">
    <meta name="author" content="krysros">
    <link rel="icon" href="${request.static_url('marker:static/img/logo-K.svg')}" type="image/svg+xml">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.0/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-gH2yIJqKdNHPEq0n4Mqa/HGKIhSkIHeL5AyhkYV8i59U5AR6csBvApHHNl/vI1Bx" crossorigin="anonymous">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.9.1/font/bootstrap-icons.css">
    % if title:
    <title>Marker - ${title}</title>
    % else:
    <title>Marker</title>
    % endif
    <style>
      body {
        padding-top: 5rem;
      }
      .nav-tabs {
        margin-bottom: 20px;
      }
      .card {
        margin-bottom: 20px;
      }
      tr.htmx-swapping td {
        opacity: 0;
        transition: opacity 1s ease-out;
      }
    </style>
  </head>
  <body>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.0/dist/js/bootstrap.bundle.min.js" integrity="sha384-A3rJD856KowSb7dwlZdYEkO39Gagi7vIsF0jrRAoQmDKKtQBHUuLZ9AsSv4jD4Xa" crossorigin="anonymous"></script>
    <script src="https://unpkg.com/htmx.org@1.8.0" integrity="sha384-cZuAZ+ZbwkNRnrKi05G/fjBX+azI9DNOkNYysZ0I/X5ZFgsmMiBXgDZof30F5ofc" crossorigin="anonymous"></script>

    <form id="logout" action="${request.route_url('logout')}" method="post">
      <input type="hidden" name="csrf_token" value="${request.session.get_csrf_token()}">
    </form>

    <nav class="navbar navbar-expand-md fixed-top bg-light">
      <div class="container-fluid">
        <a class="navbar-brand" href="${request.route_url('home')}">Marker</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto mb-2 mb-md-0">
            <li class="nav-item">
              <a class="nav-link" role="button" hx-get="${request.route_url('company_all')}" hx-target="#main-container"><i class="bi bi-building"></i> Firmy</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" role="button" hx-get="${request.route_url('project_all')}" hx-target="#main-container"><i class="bi bi-briefcase"></i> Projekty</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" role="button" hx-get="${request.route_url('tag_all')}" hx-target="#main-container"><i class="bi bi-tags"></i> Tagi</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" role="button" hx-get="${request.route_url('person_all')}" hx-target="#main-container"><i class="bi bi-people"></i> Osoby</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" role="button" hx-get="${request.route_url('user_all')}" hx-target="#main-container"><i class="bi bi-person-circle"></i> Użytkownicy</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" role="button" hx-get="${request.route_url('comment_all')}" hx-target="#main-container"><i class="bi bi-chat-left-text"></i> Komentarze</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" role="button" hx-get="${request.route_url('report')}" hx-target="#main-container"><i class="bi bi-bar-chart"></i> Raporty</a>
            </li>
          </ul>
          <ul class="navbar-nav ms-auto">
            % if not request.is_authenticated:
            <li class="nav-item">
              <a class="nav-link" href="${request.application_url}/login">Zaloguj</a>
            </li>
            % else:
            <li class="nav-item dropdown">
              <a class="nav-link dropdown-toggle" href="#" role="button" id="dropdown-account" data-bs-toggle="dropdown" aria-expanded="false">
                <i class="bi bi-person-circle"></i> ${request.identity.name}
              </a>
              <ul class="dropdown-menu dropdown-menu-end">
                <li>
                  <a class="dropdown-item" role="button" hx-get="${request.route_url('user_checked', username=request.identity.name)}" hx-target="#main-container">
                    <i class="bi bi-check-square"></i> Zaznaczone
                  </a>
                </li>
                <li>
                  <a class="dropdown-item" role="button" hx-get="${request.route_url('user_recomended', username=request.identity.name)}" hx-target="#main-container">
                    <i class="bi bi-hand-thumbs-up"></i> Rekomendowane
                  </a>
                </li>
                <li>
                  <a class="dropdown-item" role="button" hx-get="${request.route_url('user_watched', username=request.identity.name)}" hx-target="#main-container">
                    <i class="bi bi-eye"></i> Obserwowane
                  </a>
                </li>
                <li><hr class="dropdown-divider"></li>
                <li>
                  <a class="dropdown-item" role="button" hx-get="${request.route_url('account', username=request.identity.name)}" hx-target="#main-container">
                    Konto
                  </a>
                </li>
                <li><hr class="dropdown-divider"></li>
                <li>
                  <a class="dropdown-item" href="#" onclick="javascript:document.getElementById('logout').submit();">
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

    <main role="main">
      <div id="main-container" class="container">
        % if request.session.peek_flash():
          % for message in request.session.pop_flash():
            <div class="alert alert-${message.split(':')[0]}" role="alert">
              ${message.split(':')[1] | n}
            </div>
          % endfor
        % endif
        ${self.body()}
      </div>
    </main>

    <footer class="container">
      <hr>
      <p>
        <div class="d-flex">
          <div class="p-2 flex-grow-1">© KR 2022</div>
          <div class="p-2"><a href="#top"><i class="bi bi-arrow-up"></i> Do góry</a></div>
        </div>
      </p>
    </footer>

  </body>
</html>