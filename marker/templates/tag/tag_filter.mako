<div class="dropdown">
  <button type="button" class="btn btn-secondary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside">
    <i class="bi bi-filter"></i> ${_("Filter")}
  </button>
  <form class="dropdown-menu p-4" style="min-width: 420px;">
    % if form.name.data:
      ${form.name()}
    % endif
    <div class="mb-3">
      ${form.category.label(class_="form-label")}
      ${form.category(class_="form-control")}
    </div>
    <div class="mb-3">
      <label class="form-label">${_("Date")}</label>
      <div class="input-group">
        ${form.date_from(class_="form-control", placeholder=_("From"))}
        ${form.date_to(class_="form-control", placeholder=_("To"))}
      </div>
    </div>
    <div class="hstack gap-2">
      <button type="submit" class="btn btn-primary">${_("Submit")}</button>
      <% clear_q = {k: v for k, v in q.items() if k in ('sort', 'order')} %>
      <a class="btn btn-outline-secondary" href="${request.current_route_url(_query=clear_q)}">${_("Clear")}</a>
    </div>
  </form>
</div>
