<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-buildings"></i> ${_("Companies")} — ${_("Website check")}
  <span class="badge bg-secondary">${len(items)}</span>
  <div class="float-end">
    ${button.a(icon='table', color='secondary', url=request.route_url('company_all'))}
    ${button.a(icon='search', color='primary', url=request.route_url('company_search'))}
    ${button.a(icon='plus-lg', color='success', url=request.route_url('company_add'))}
  </div>
</h2>
<hr>

<div class="mb-3">
  <button id="btn-start-stop" class="btn btn-success" onclick="toggleCheck()">
    <i class="bi bi-play-fill"></i> Start
  </button>
  <span id="progress-info" class="ms-2 text-muted"></span>
</div>

<div class="table-responsive">
<table class="table table-striped">
  <thead>
    <tr>
      <th>#</th>
      <th>${_("Name")}</th>
      <th>${_("Website")}</th>
      <th>${_("HTTP response code")}</th>
    </tr>
  </thead>
  <tbody id="uptime-tbody">
    % for i, item in enumerate(items, 1):
    <tr>
      <td>${i}</td>
      <td>${item['name']}</td>
      <td class="text-break"><a href="${item['website'] if item['website'].startswith(('http://', 'https://')) else 'https://' + item['website']}" target="_blank" rel="noopener">${item['website']}</a></td>
      <td class="status-cell" data-url="${item['website']}">
        <span class="badge bg-secondary">${_("Waiting...")}</span>
      </td>
    </tr>
    % endfor
  </tbody>
</table>
</div>

<script>
  var checkUrl = "${request.route_url('company_uptime_check')}";
  var running = false;
  var stopped = false;
  var currentIndex = 0;
  var cells = [];

  function toggleCheck() {
    var btn = document.getElementById('btn-start-stop');
    if (running) {
      stopped = true;
      running = false;
      btn.className = 'btn btn-success';
      btn.innerHTML = '<i class="bi bi-play-fill"></i> Start';
    } else {
      stopped = false;
      running = true;
      btn.className = 'btn btn-danger';
      btn.innerHTML = '<i class="bi bi-stop-fill"></i> Stop';
      cells = document.querySelectorAll('.status-cell');
      runChecks();
    }
  }

  function badgeClass(code) {
    if (code === null || code === undefined) return 'bg-dark';
    if (code >= 200 && code < 300) return 'bg-success';
    if (code >= 300 && code < 400) return 'bg-info';
    if (code === 403) return 'bg-warning';
    if (code === 404) return 'bg-dark';
    if (code >= 400 && code < 500) return 'bg-warning';
    if (code >= 500) return 'bg-danger';
    return 'bg-secondary';
  }

  function updateProgress() {
    var total = cells.length;
    var info = document.getElementById('progress-info');
    info.textContent = currentIndex + ' / ' + total;
  }

  async function runChecks() {
    cells = document.querySelectorAll('.status-cell');
    for (var i = currentIndex; i < cells.length; i++) {
      if (stopped) return;
      currentIndex = i;
      var cell = cells[i];
      var url = cell.getAttribute('data-url');
      cell.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Loading...</span></div>';
      try {
        var resp = await fetch(checkUrl + '?url=' + encodeURIComponent(url));
        var data = await resp.json();
        if (data.status_code !== null) {
          cell.innerHTML = '<span class="badge ' + badgeClass(data.status_code) + '">' + data.status_code + '</span>';
        } else {
          cell.innerHTML = '<span class="badge bg-dark" title="' + (data.error || 'Error') + '">${_("Error")}</span>';
        }
      } catch (e) {
        cell.innerHTML = '<span class="badge bg-dark">${_("Error")}</span>';
      }
      currentIndex = i + 1;
      updateProgress();
    }
    running = false;
    var btn = document.getElementById('btn-start-stop');
    btn.className = 'btn btn-success';
    btn.innerHTML = '<i class="bi bi-play-fill"></i> Start';
  }
</script>
