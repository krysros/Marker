<%inherit file="../base/layout.mako"/>

<%include file="../base/flash_messages.mako"/>

<div class="card mt-4 mb-4">
  <div class="card-header">${heading}</div>
  <div class="card-body">
    <form method="post" hx-post="${request.route_url('project_add_ai')}">
      <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
      <div class="mb-3">
        ${form.website.label(class_="form-label")}
        ${form.website(class_="form-control")}
        % for error in form.errors.get("website", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>
      <div class="mb-3">
        <button id="submit-btn" type="submit" class="btn btn-primary" hx-disable>
          <span id="submit-spinner" class="spinner-grow spinner-grow-sm me-2 d-none" role="status" aria-hidden="true"></span>
          <span id="submit-btn-text">${_("Submit")}</span>
        </button>
      </div>
      <script>
        document.addEventListener('htmx:configRequest', function(evt) {
          var btn = document.getElementById('submit-btn');
          var spinner = document.getElementById('submit-spinner');
          if (btn && spinner) {
            btn.setAttribute('disabled', 'disabled');
            spinner.classList.remove('d-none');
          }
        });
      </script>
    </form>
  </div>
</div>  