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
    <script src="${request.static_url('marker:static/js/marker-focus-first-input.js')}"></script>
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
                <li class="list-group-item list-group-item-action d-flex align-items-center" data-url="${request.route_url('company_search')}"><span><i class="bi bi-buildings"></i> ${_("Companies")}</span><kbd class="ms-auto">1</kbd></li>
                <li class="list-group-item list-group-item-action d-flex align-items-center" data-url="${request.route_url('project_search')}"><span><i class="bi bi-briefcase"></i> ${_("Projects")}</span><kbd class="ms-auto">2</kbd></li>
                <li class="list-group-item list-group-item-action d-flex align-items-center" data-url="${request.route_url('tag_search')}"><span><i class="bi bi-tags"></i> ${_("Tags")}</span><kbd class="ms-auto">3</kbd></li>
                <li class="list-group-item list-group-item-action d-flex align-items-center" data-url="${request.route_url('contact_search')}"><span><i class="bi bi-people"></i> ${_("Contacts")}</span><kbd class="ms-auto">4</kbd></li>
                <li class="list-group-item list-group-item-action d-flex align-items-center" data-url="${request.route_url('comment_search')}"><span><i class="bi bi-chat-left-text"></i> ${_("Comments")}</span><kbd class="ms-auto">5</kbd></li>
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
                <li class="list-group-item list-group-item-action d-flex align-items-center" data-url="${request.route_url('company_add')}"><span><i class="bi bi-buildings"></i> ${_("Company")}</span><kbd class="ms-auto">1</kbd></li>
                <li class="list-group-item list-group-item-action d-flex align-items-center" data-url="${request.route_url('project_add')}"><span><i class="bi bi-briefcase"></i> ${_("Project")}</span><kbd class="ms-auto">2</kbd></li>
                <li class="list-group-item list-group-item-action d-flex align-items-center" data-url="${request.route_url('tag_add')}"><span><i class="bi bi-tags"></i> ${_("Tag")}</span><kbd class="ms-auto">3</kbd></li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <!-- Shortcuts Modal -->
      <div class="modal fade" id="shortcutsModal" tabindex="-1" aria-labelledby="shortcutsModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered modal-lg">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title" id="shortcutsModalLabel">${_("Keyboard Shortcuts")}</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              <div class="table-responsive">
                <table class="table table-sm align-middle mb-0">
                  <thead>
                    <tr>
                      <th scope="col">${_("Shortcut")}</th>
                      <th scope="col">${_("Action")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td><kbd>/</kbd></td>
                      <td>${_("Open search or focus search input")}</td>
                    </tr>
                    <tr>
                      <td><kbd>+</kbd> / <kbd>Insert</kbd></td>
                      <td>${_("Open add menu or add new item")}</td>
                    </tr>
                    <tr>
                      <td><kbd>-</kbd> / <kbd>Delete</kbd></td>
                      <td>${_("Delete selected item (if available)")}</td>
                    </tr>
                    <tr>
                      <td><kbd>Home</kbd></td>
                      <td>${_("Go to homepage")}</td>
                    </tr>
                    <tr>
                      <td><kbd>1</kbd>–<kbd>5</kbd></td>
                      <td>${_("Quick navigation to main sections (on homepage)")}</td>
                    </tr>
                    <tr>
                      <td><kbd>*</kbd></td>
                      <td>${_("Toggle star for company/project")}</td>
                    </tr>
                    <tr>
                      <td><kbd>Arrow keys</kbd> / <kbd>Enter</kbd></td>
                      <td>${_("Navigate and select in modals")}</td>
                    </tr>
                    <tr>
                      <td><kbd>Esc</kbd></td>
                      <td>${_("Close modal")}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
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