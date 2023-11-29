<%!
  from sqlalchemy import select
  from marker.models import Theme
%>

<%
  theme = "light"
  if request.identity:
    stmt = select(Theme.theme).filter(Theme.user_id == request.identity.id)
    theme = request.dbsession.execute(stmt).scalar_one_or_none()
    if not theme:
      theme = "light"
      t = Theme(user_id=request.identity.id, theme=theme)
      request.dbsession.add(t)
%>

<!doctype html>
<html lang="${request.locale_name}" data-bs-theme="${theme}">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="Informacje o firmach i projektach">
    <meta name="author" content="krysros">
    <link rel="icon" href="${request.static_url('marker:static/img/logo-K.svg')}" type="image/svg+xml">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN" crossorigin="anonymous">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-C6RzsynM9kWDrMNeT87bh95OGNyZPhcTNXj1NW7RuBCsyN/o0jlpcV8Qyq46cDfL" crossorigin="anonymous"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.2/font/bootstrap-icons.min.css">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.css"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.Default.css"></script>
    <script src="https://unpkg.com/leaflet.markercluster@1.4.1/dist/leaflet.markercluster.js"></script>
    <script src="https://unpkg.com/htmx.org@1.9.9" integrity="sha384-QFjmbokDn2DjBjq+fM+8LUIVrAgqcNW2s0PjAxHETgRn9l4fvX31ZxDxvwQnyMOX" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/qrcode-svg@1.1.0/dist/qrcode.min.js"></script>
    % if title:
    <title>Marker - ${title}</title>
    % else:
    <title>Marker</title>
    % endif
    <style>
      body {
        padding-top: 5rem;
      }
      tr.htmx-swapping td {
        opacity: 0;
        transition: opacity 1s ease-out;
      }
      .card.htmx-swapping {
        opacity: 0;
        transition: opacity 1s ease-out;
      }
      #map { height: 400px; }
    </style>
  </head>
  <body>
    <main role="main">
      <div class="container">
        <%include file="navbar.mako" args="theme=theme"/>
        <%include file="flash_messages.mako"/>
        ${self.body()}
        <%include file="footer.mako"/>
      </div>
    </main>
  </body>
</html>