<%inherit file="layout.mako"/>

<h2><i class="bi bi-speedometer2"></i> ${heading}</h2>
<hr>

<div class="row g-3 mb-3">
  <div class="col-sm-6 col-lg-3">
    <div class="card h-100">
      <div class="card-body">
        <h6 class="card-title text-body-secondary">${_('Requests')}</h6>
        <div class="display-6">${totals.get('requests', 0)}</div>
      </div>
    </div>
  </div>
  <div class="col-sm-6 col-lg-3">
    <div class="card h-100">
      <div class="card-body">
        <h6 class="card-title text-body-secondary">${_('Errors')}</h6>
        <div class="display-6">${totals.get('errors', 0)}</div>
      </div>
    </div>
  </div>
  <div class="col-sm-6 col-lg-3">
    <div class="card h-100">
      <div class="card-body">
        <h6 class="card-title text-body-secondary">${_('Error rate')}</h6>
        <div class="display-6">${totals.get('error_rate_pct', 0)}%</div>
      </div>
    </div>
  </div>
  <div class="col-sm-6 col-lg-3">
    <div class="card h-100">
      <div class="card-body">
        <h6 class="card-title text-body-secondary">${_('Avg latency')}</h6>
        <div class="display-6">${totals.get('avg_latency_ms', 0)} ms</div>
      </div>
    </div>
  </div>
</div>

<div class="table-responsive">
  <table class="table table-striped table-sm align-middle">
    <thead>
      <tr>
        <th>${_('Source')}</th>
        <th>${_('Requests')}</th>
        <th>${_('Success')}</th>
        <th>${_('Errors')}</th>
        <th>${_('Retries')}</th>
        <th>${_('Error rate')}</th>
        <th>${_('Avg latency')}</th>
        <th>${_('Tokens')}</th>
        <th>${_('Last model')}</th>
        <th>${_('Last error')}</th>
      </tr>
    </thead>
    <tbody>
      % if not sources:
      <tr>
        <td colspan="10" class="text-center text-body-secondary">${_('No telemetry data yet.')}</td>
      </tr>
      % endif
      % for row in sources:
      <tr>
        <td>${row.get('source') or 'unknown'}</td>
        <td>${row.get('requests', 0)}</td>
        <td>${row.get('success', 0)}</td>
        <td>${row.get('errors', 0)}</td>
        <td>${row.get('retries', 0)}</td>
        <td>${row.get('error_rate_pct', 0)}%</td>
        <td>${row.get('avg_latency_ms', 0)} ms</td>
        <td>${row.get('total_tokens', 0)}</td>
        <td>${row.get('last_model') or '---'}</td>
        <td class="text-truncate" style="max-width: 28rem;">${row.get('last_error') or '---'}</td>
      </tr>
      % endfor
    </tbody>
  </table>
</div>
