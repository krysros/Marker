<%def name="danger_dialog(route_name, title, body, **kwargs)">
<!-- Button trigger modal -->
<button type="button" class="btn btn-danger" data-bs-toggle="modal" data-bs-target="#${route_name}_modal">
  ${title}
</button>

<!-- Modal -->
<div class="modal fade" id="${route_name}_modal" tabindex="-1" aria-labelledby="${route_name}_modal_label" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="${route_name}_modal_label">${title}</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
      </div>
      <div class="modal-body">
        ${body}
      </div>
      <div class="modal-footer">
        <form hx-post="${request.route_url(route_name, **kwargs)}" hx-target="#main-container">
          <input type="hidden" name="csrf_token" value="${request.session.get_csrf_token()}">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Nie</button>
          <button type="submit" class="btn btn-primary" name="submit" value="delete">Tak</button>
        </form>
      </div>
    </div>
  </div>
</div>
</%def>