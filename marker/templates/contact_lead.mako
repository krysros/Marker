<div class="hstack">
  <div class="me-auto">
    <p class="lead">
      % if contact in request.identity.selected_contacts:
      <input class="form-check-input"
            id="mark"
            type="checkbox"
            value="${contact.id}"
            autocomplete="off"
            checked
            hx-post="${request.route_url('contact_check', contact_id=contact.id)}"
            hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
            hx-trigger="click"
            hx-swap="none">
      % else:
      <input class="form-check-input"
            id="mark"
            type="checkbox"
            value="${contact.id}"
            autocomplete="off"
            hx-post="${request.route_url('contact_check', contact_id=contact.id)}"
            hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
            hx-trigger="click"
            hx-swap="none">
      % endif
      &nbsp;${contact.name}
    </p>
  </div>
</div>