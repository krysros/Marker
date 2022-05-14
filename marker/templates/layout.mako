<!DOCTYPE html>
<html lang="${request.locale_name}">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="description" content="Informacje o firmach i inwestycjach">
    <meta name="author" content="krysros">
    <meta name="csrf_token" content="${request.session.get_csrf_token()}">
    <link rel="shortcut icon" href="${request.static_url('marker:static/img/favicon.png')}">
    % if title:
    <title>Marker - ${title}</title>
    % else:
    <title>Marker</title>
    % endif
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <link rel="stylesheet" href="${request.static_url('deform:static/css/bootstrap.min.css')}">
    <link rel="stylesheet" href="${request.static_url('deform:static/css/form.css')}">
    % if css_links:
      % for reqt in css_links:
      <link rel="stylesheet" href="${request.static_url(reqt)}">
      % endfor
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
    </style>
    <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!--[if lt IE 9]>
      <script src="//oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
      <script src="//oss.maxcdn.com/libs/respond.js/1.3.0/respond.min.js"></script>
    <![endif]-->
  </head>
  <body>
    <script src="${request.static_url('deform:static/scripts/jquery-2.0.3.min.js')}" type="text/javascript"></script>
    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js" type="text/javascript"></script>
    <script src="${request.static_url('deform:static/scripts/bootstrap.min.js')}" type="text/javascript"></script>
    <script src="https://unpkg.com/htmx.org@1.7.0" integrity="sha384-EzBXYPt0/T6gxNp0nuPtLkmRpmDBbjg6WmCUZRLXBBwYYmwAUxzlSGej0ARHX0Bo" crossorigin="anonymous"></script>
    % if js_links:
      % for reqt in js_links:
      <script src="${request.static_url(reqt)}" type="text/javascript"></script>
      % endfor
    % endif

    <form id="logout" action="${request.route_url('logout')}" method="post">
      <input type="hidden" name="csrf_token" value="${request.session.get_csrf_token()}">
    </form>

    <nav class="navbar navbar-expand-md navbar-dark fixed-top bg-dark">
      <a class="navbar-brand" href="${request.route_url('home')}">Marker</a>
      <button class="navbar-toggler" type="button" data-toggle="collapse" data-target=".navbar-collapse" aria-controls="navbar-collapse" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbar-collapse">
        <ul class="navbar-nav ml-auto">
          <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" id="dropdown-db" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              <i class="fa fa-puzzle-piece" aria-hidden="true"></i> Moduły
            </a>
            <div class="dropdown-menu" aria-labelledby="dropdown-db">
              <a class="dropdown-item" href="${request.route_url('branch_all')}"><i class="fa fa-cubes" aria-hidden="true"></i> Branże</a>
              <a class="dropdown-item" href="${request.route_url('company_all')}"><i class="fa fa-industry" aria-hidden="true"></i> Firmy</a>
              <a class="dropdown-item" href="${request.route_url('investment_all')}"><i class="fa fa-briefcase" aria-hidden="true"></i> Inwestycje</a>
              <a class="dropdown-item" href="${request.route_url('user_all')}"><i class="fa fa-users" aria-hidden="true"></i> Użytkownicy</a>
              <a class="dropdown-item" href="${request.route_url('comment_all')}"><i class="fa fa-comments" aria-hidden="true"></i> Komentarze</a>
              <a class="dropdown-item" href="${request.route_url('document_all')}"><i class="fa fa-file-word-o" aria-hidden="true"></i> Dokumenty</a>
              <a class="dropdown-item" href="${request.route_url('report')}"><i class="fa fa-line-chart" aria-hidden="true"></i> Raporty</a>
            </div>
          </li>
          <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" id="dropdown-add" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              <i class="fa fa-plus" aria-hidden="true"></i> Dodaj
            </a>
            <div class="dropdown-menu" aria-labelledby="dropdown-add">
              <a class="dropdown-item" href="${request.route_url('branch_add')}"><i class="fa fa-cube" aria-hidden="true"></i> branżę</a>
              <a class="dropdown-item" href="${request.route_url('company_add')}"><i class="fa fa-industry" aria-hidden="true"></i> firmę</a>
              <a class="dropdown-item" href="${request.route_url('investment_add')}"><i class="fa fa-briefcase" aria-hidden="true"></i> inwestycję</a>
              <a class="dropdown-item" href="${request.route_url('user_add')}"><i class="fa fa-user" aria-hidden="true"></i> użytkownika</a>
              <a class="dropdown-item" href="${request.route_url('document_upload')}"><i class="fa fa-file-word-o" aria-hidden="true"></i> dokument</a>
            </div>
          </li>
          <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" id="dropdown-search" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              <i class="fa fa-search" aria-hidden="true"></i> Szukaj
            </a>
            <div class="dropdown-menu" aria-labelledby="dropdown-search">
              <a class="dropdown-item" href="${request.route_url('branch_search')}"><i class="fa fa-cube" aria-hidden="true"></i> branżę</a>
              <a class="dropdown-item" href="${request.route_url('company_search')}"><i class="fa fa-industry" aria-hidden="true"></i> firmę</a>
              <a class="dropdown-item" href="${request.route_url('investment_search')}"><i class="fa fa-briefcase" aria-hidden="true"></i> inwestycję</a>
              <a class="dropdown-item" href="${request.route_url('person_search')}"><i class="fa fa-user-o" aria-hidden="true"></i> osobę</a>
              <a class="dropdown-item" href="${request.route_url('user_search')}"><i class="fa fa-user" aria-hidden="true"></i> użytkownika</a>
              <a class="dropdown-item" href="${request.route_url('comment_search')}"><i class="fa fa-comment" aria-hidden="true"></i> komentarz</a>
            </div>
          </li>
          % if not request.is_authenticated:
          <li class="nav-item"><a class="nav-link" href="${request.application_url}/login">Zaloguj</a></li>
          % else:
          <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" id="dropdown-account" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              <i class="fa fa-user" aria-hidden="true"></i> ${request.identity.username}
            </a>
            <div class="dropdown-menu dropdown-menu-right" aria-labelledby="dropdown-account">
              <a class="dropdown-item" href="${request.route_url('user_marked', username=request.identity.username)}">
                <i class="fa fa-check-square-o" aria-hidden="true"></i> Zaznaczone
              </a>
              <a class="dropdown-item" href="${request.route_url('user_upvotes', username=request.identity.username)}">
                <i class="fa fa-thumbs-up" aria-hidden="true"></i> Rekomendowane
              </a>
              <a class="dropdown-item" href="${request.route_url('user_following', username=request.identity.username)}">
                <i class="fa fa-eye" aria-hidden="true"></i> Obserwowane
              </a>
              <div class="dropdown-divider"></div>
              <a class="dropdown-item" href="${request.route_url('account', username=request.identity.username)}">
                <i class="fa fa-edit" aria-hidden="true"></i> Konto
              </a>
              <div class="dropdown-divider"></div>
              <a class="dropdown-item" href="#" onclick="javascript:document.getElementById('logout').submit();">
                <i class="fa fa-sign-out" aria-hidden="true"></i> Wyloguj
              </a>
            </div>
          </li>
          % endif
        </ul>
      </div>
    </nav>

    <main role="main">
      <div class="container">
        % if request.session.peek_flash():
          % for message in request.session.pop_flash():
            <div class="alert alert-${message.split(':')[0]}" role="alert">
              ${message.split(':')[1] | n}
            </div>
          % endfor
        % endif
        ${self.body()}
        <hr>
      </div>
    </main>

    <footer class="container">
      <p class="float-right"><a href="#top"><i class="fa fa-arrow-up"></i> Do góry</a></p>
      <p><i class="fa fa-copyright"></i> KR 2022</p>
    </footer>

  </body>
</html>