<!doctype html>
<html lang="${request.locale_name}">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="Informacje o firmach i projektach">
    <meta name="author" content="krysros">
    <link rel="icon" href="${request.static_url('marker:static/img/logo-K.svg')}" type="image/svg+xml">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-Zenh87qX5JnK2Jl0vWa8Ck2rdkQ2Bzep5IDxbcnCeuOxjzrPF/et3URy9Bv1WTRi" crossorigin="anonymous">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.9.1/font/bootstrap-icons.css">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.1/dist/leaflet.css" integrity="sha256-sA+zWATbFveLLNqWO2gtiw3HL/lh1giY/Inf1BJ0z14=" crossorigin="">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-OERcA2EqjJCMA+/3y+gxIOqMEjwtxJY7qPCqsdltbNJuaOe923+mo//f6V8Qbsw3" crossorigin="anonymous"></script>
    <script src="https://unpkg.com/leaflet@1.9.1/dist/leaflet.js" integrity="sha256-NDI0K41gVbWqfkkaHj15IzU7PtMoelkzyKp8TOaFQ3s=" crossorigin=""></script>
    <script src="https://unpkg.com/htmx.org@1.8.2" integrity="sha384-+8ISc/waZcRdXCLxVgbsLzay31nCdyZXQxnsUy++HJzJliTzxKWr0m1cIEMyUzQu" crossorigin="anonymous"></script>
    % if title:
    <title>Marker - ${title}</title>
    % else:
    <title>Marker</title>
    % endif
    <style>
      body {
        padding-top: 5rem;
      }
      .card {
        margin-bottom: 30px;
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
        <%include file="navbar.mako"/>
        <%include file="flash_messages.mako"/>
        ${self.body()}
        <%include file="footer.mako"/>
      </div>
    </main>
  </body>
</html>