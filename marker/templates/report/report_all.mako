<%inherit file="layout.mako"/>

<h2>
  <i class="bi bi-bar-chart"></i> ${_("Reports")}
  <span class="badge bg-secondary">${counter}</span>
</h2>

<hr>

<input
  type="search"
  id="report-filter"
  class="form-control mb-3"
  placeholder="${_('Search reports...')}"
  list="reports-datalist"
  autocomplete="off"
>
<datalist id="reports-datalist">
  % for rel, report in reports:
  <option value="${report}"></option>
  % endfor
</datalist>

<ol class="list-group list-group-numbered" id="reports-list">
  % for rel, report in reports:
  <a class="list-group-item list-group-item-action" href="${request.route_url('report_view', rel=rel)}" data-report-name="${_(report).lower()}">${report}</a>
  % endfor
</ol>

<script>
document.getElementById('report-filter').addEventListener('input', function () {
  var q = this.value.toLowerCase();
  document.querySelectorAll('#reports-list a').forEach(function (el) {
    el.style.display = el.dataset.reportName.includes(q) ? '' : 'none';
  });
});
</script>
