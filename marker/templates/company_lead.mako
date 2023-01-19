<div class="hstack">
  <div class="me-auto">
    <p class="lead">
      % if company in request.identity.checked:
      <input class="form-check-input"
            id="mark"
            type="checkbox"
            value="${company.id}"
            autocomplete="off"
            checked
            hx-post="${request.route_url('company_check', company_id=company.id)}"
            hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
            hx-trigger="click"
            hx-swap="none">
      % else:
      <input class="form-check-input"
            id="mark"
            type="checkbox"
            value="${company.id}"
            autocomplete="off"
            hx-post="${request.route_url('company_check', company_id=company.id)}"
            hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
            hx-trigger="click"
            hx-swap="none">
      % endif
      &nbsp;${company.name}
    </p>
  </div>
</div>