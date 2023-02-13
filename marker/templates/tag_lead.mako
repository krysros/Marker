<div class="hstack">
  <div class="me-auto">
    <p class="lead">
      % if tag in request.identity.selected_tags:
      <input class="form-check-input"
            id="mark"
            type="checkbox"
            value="${tag.id}"
            autocomplete="off"
            checked
            hx-post="${request.route_url('tag_check', tag_id=tag.id)}"
            hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
            hx-trigger="click"
            hx-swap="none">
      % else:
      <input class="form-check-input"
            id="mark"
            type="checkbox"
            value="${tag.id}"
            autocomplete="off"
            hx-post="${request.route_url('tag_check', tag_id=tag.id)}"
            hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
            hx-trigger="click"
            hx-swap="none">
      % endif
      &nbsp;${tag.name}
    </p>
  </div>
</div>