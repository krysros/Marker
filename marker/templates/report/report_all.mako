<%inherit file="layout.mako"/>

<h2>
  <i class="bi bi-bar-chart"></i> ${_("Reports")}
  <span class="badge bg-secondary">${counter}</span>
</h2>

<hr>

<ol class="list-group list-group-numbered">
  % for rel, report in reports:
  <a class="list-group-item list-group-item-action" href="${request.route_url('report_view', rel=rel)}">${report}</a>
  % endfor
</ol>
