<%inherit file="layout.mako"/>

<div class="card mt-4 mb-4">
  <div class="card-header">${heading}</div>
  <div class="card-body">
    <form action="${request.current_route_path()}" method="post">
      <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
      <div class="mb-3">
        ${form.name.label(class_="form-label")}
        ${form.name(class_="form-control" + (" is-invalid" if form.errors.get("name") else ""))}
        % for error in form.errors.get("name", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>
      <div class="mb-3">
        % if request.matched_route and request.matched_route.name == 'tag_search_ai':
          <button type="submit" class="btn btn-primary" onclick="this.classList.add('disabled'); this.querySelector('.spinner-grow').classList.remove('d-none');">
            <span class="spinner-grow spinner-grow-sm me-2 d-none" role="status" aria-hidden="true"></span>
            ${_("Submit")}
          </button>
        % else:
          <button type="submit" class="btn btn-primary">${_("Submit")}</button>
        % endif
      </div>
    </form>
  </div>
</div>