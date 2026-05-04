<%inherit file="layout.mako"/>

<h2>
  <i class="bi bi-robot"></i> ${_("Prompt")}
</h2>

<hr>

% if not gemini_api_key_set:
<div class="alert alert-warning" role="alert">
  <i class="bi bi-exclamation-triangle"></i>
  ${_("GEMINI_API_KEY is not set. AI reports require a valid Gemini API key configured on the server.")}
</div>
% endif

<form method="POST" action="${request.route_url('prompt')}">
  <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
  <div class="mb-3">
    <label for="ai-prompt" class="form-label fw-semibold">
      <i class="bi bi-chat-left-text"></i> ${_("Describe the report you want:")}
    </label>
    <textarea
      class="form-control font-monospace"
      id="ai-prompt"
      name="prompt"
      rows="4"
      placeholder="${_('e.g. Show top 10 companies by number of projects')}"
    >${prompt | h}</textarea>
  </div>
  <button type="submit" class="btn btn-primary" ${'disabled' if not gemini_api_key_set else ''}>
    <i class="bi bi-robot"></i> ${_("Generate")}
  </button>
</form>

% if error:
<div class="alert alert-danger mt-4" role="alert">
  <i class="bi bi-exclamation-circle"></i>
  <strong>${_("Error")}:</strong> ${error | h}
</div>
% endif

% if sql_generated:
<div class="mt-4">
  <h5 class="text-body-secondary"><i class="bi bi-code-slash"></i> ${_("Generated SQL")}</h5>
  <pre class="bg-body-secondary p-3 rounded small"><code>${sql_generated | h}</code></pre>
</div>
% endif

% if columns is not None:
<div class="mt-4">
  <h5>
    <i class="bi bi-table"></i> ${_("Results")}
    <span class="badge bg-secondary">${len(rows)}</span>
  </h5>
  % if rows:
  <div class="table-responsive">
    <table class="table table-striped table-sm">
      <thead>
        <tr>
          % for col in columns:
          <th>${col}</th>
          % endfor
        </tr>
      </thead>
      <tbody>
        % for row in rows:
        <tr>
          % for cell in row:
          <td>${cell if cell is not None else "---"}</td>
          % endfor
        </tr>
        % endfor
      </tbody>
    </table>
  </div>
  % else:
  <p class="text-body-secondary">${_("No results.")}</p>
  % endif
% endif
