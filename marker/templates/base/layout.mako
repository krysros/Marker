<!doctype html>
<html lang="${request.locale_name}" data-bs-theme="auto">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="Informacje o firmach i projektach">
    <meta name="author" content="krysros">
    <link rel="icon" href="${request.static_url('marker:static/img/logo-K.svg')}" type="image/svg+xml">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB" crossorigin="anonymous">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js" integrity="sha384-FKyoEForCGlyvwx9Hj09JcYn3nv7wiPVlz7YYwJrWVcXK/BmnVDxM+D2scQbITxI" crossorigin="anonymous"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/bootstrap-icons.min.css">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.css">
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.Default.css">
    <script src="https://unpkg.com/leaflet.markercluster@1.4.1/dist/leaflet.markercluster.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.8/dist/htmx.min.js" integrity="sha384-/TgkGk7p307TH7EXJDuUlgG3Ce1UVolAOFopFekQkkXihi5u/6OCvVKyz1W+idaz" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/qrcode-svg@1.1.0/dist/qrcode.min.js"></script>
    <script src="https://getbootstrap.com/docs/5.3/assets/js/color-modes.js"></script>
    <script src="${request.static_url('marker:static/js/marker-select-all-state.js')}"></script>
    <script src="${request.static_url('marker:static/js/marker-website-autofill.js')}"></script>
    <link rel="stylesheet" href="${request.static_url('marker:static/css/style.css')}">
    <script src="${request.static_url('marker:static/js/shortcuts.js')}"></script>
    % if title:
    <title>Marker - ${title}</title>
    % else:
    <title>Marker</title>
    % endif
  </head>
  <body>
    <main role="main">
      <div class="container">
        <%include file="svg_icons.mako"/>
        <%include file="navbar.mako"/>
        <%include file="flash_messages.mako"/>
        ${self.body()}
        <%include file="footer.mako"/>
      </div>
      <!-- Search Selection Modal -->
      <div class="modal fade" id="searchSelectModal" tabindex="-1" aria-labelledby="searchSelectModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title" id="searchSelectModalLabel">${_("Select what to search")}</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              <ul class="list-group" id="searchSelectList">
                <li class="list-group-item list-group-item-action" data-url="${request.route_url('company_search')}"><i class="bi bi-buildings"></i> ${_("Companies")} <span class="text-muted">[1]</span></li>
                <li class="list-group-item list-group-item-action" data-url="${request.route_url('project_search')}"><i class="bi bi-briefcase"></i> ${_("Projects")} <span class="text-muted">[2]</span></li>
                <li class="list-group-item list-group-item-action" data-url="${request.route_url('tag_search')}"><i class="bi bi-tags"></i> ${_("Tags")} <span class="text-muted">[3]</span></li>
                <li class="list-group-item list-group-item-action" data-url="${request.route_url('contact_search')}"><i class="bi bi-people"></i> ${_("Contacts")} <span class="text-muted">[4]</span></li>
                <li class="list-group-item list-group-item-action" data-url="${request.route_url('comment_search')}"><i class="bi bi-chat-left-text"></i> ${_("Comments")} <span class="text-muted">[5]</span></li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <!-- Add Selection Modal -->
      <div class="modal fade" id="addSelectModal" tabindex="-1" aria-labelledby="addSelectModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title" id="addSelectModalLabel">${_("Select what to add")}</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              <ul class="list-group" id="addSelectList">
                <li class="list-group-item list-group-item-action" data-url="${request.route_url('company_add')}"><i class="bi bi-buildings"></i> ${_("Company")} <span class="text-muted">[1]</span></li>
                <li class="list-group-item list-group-item-action" data-url="${request.route_url('project_add')}"><i class="bi bi-briefcase"></i> ${_("Project")} <span class="text-muted">[2]</span></li>
                <li class="list-group-item list-group-item-action" data-url="${request.route_url('tag_add')}"><i class="bi bi-tags"></i> ${_("Tag")} <span class="text-muted">[3]</span></li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </main>
    <!-- keyboard shortcuts for pages with a single green plus or red trash button -->
    <script>
    function initPopovers(root) {
      const scope = root && root.querySelectorAll ? root : document;
      const popoverTriggers = scope.querySelectorAll('[data-bs-toggle="popover"]');
      popoverTriggers.forEach(function (el) {
        if (!bootstrap.Popover.getInstance(el)) {
          new bootstrap.Popover(el);
        }
      });
    }

    document.addEventListener('DOMContentLoaded', function(){
      initPopovers(document);
      document.body.addEventListener('htmx:afterSwap', function(e){
      initPopovers(e.target);
      });
    });
    </script>
  </body>
</html>