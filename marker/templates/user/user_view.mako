<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>

<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  <div class="me-auto">${pills.pills(user_pills)}</div>
  <div>${button.a(icon='pencil-square', color='warning', url=request.route_url('user_edit', username=user.name))}</div>
  <div class="btn-group" role="group" aria-label="${_('Delete user options')}">
    <button
      type="button"
      class="btn btn-danger"
      hx-post="${request.route_url('user_delete', username=user.name)}"
      hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
      hx-confirm='${_("Are you sure?")}'
      title="${_('Delete only the user account')}"
      aria-label="${_('Delete only the user account')}">
      <i class="bi bi-trash"></i>
    </button>
    <button
      type="button"
      class="btn btn-danger dropdown-toggle dropdown-toggle-split"
      data-bs-toggle="dropdown"
      aria-expanded="false">
      <span class="visually-hidden">${_('Toggle delete options')}</span>
    </button>
    <ul class="dropdown-menu dropdown-menu-end">
      <li>
        <button
          type="button"
          class="dropdown-item text-danger"
          hx-post="${request.route_url('user_delete', username=user.name)}"
          hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
          hx-vals='{"delete_with_data": "1"}'
          hx-confirm='${_("Delete the user account together with all data added by this user?")}'>
          <i class="bi bi-trash-fill me-2"></i>${_('Delete account with all added data')}
        </button>
      </li>
    </ul>
  </div>
</div>

<p class="lead">${user.fullname}</p>

<div class="card mt-4 mb-4">
  <div class="card-header"><i class="bi bi-person-circle"></i> ${_("User")}</div>
  <div class="card-body">
    <dl>
      <dt>${_("Name")}</dt>
      <dd>${user.name}</dd>

      <dt>${_("Fullname")}</dt>
      <dd>${user.fullname or "---"}</dd>

      <dt>${_("Email")}</dt>
      % if user.email:
      <dd><a href="mailto:${user.email}">${user.email}</a></dd>
      % else:
      <dd>---</dd>
      % endif

      <dt>${_("Role")}</dt>
      <dd>${user.role or "---"}</dd>
    </dl>
  </div>
</div>

<div class="card mt-4 mb-4">
  <div class="card-header"><i class="bi bi-clock"></i> ${_("Modification date")}</div>
  <div class="card-body">
    <p>
      ${_("Created at")}: ${user.created_at.strftime('%Y-%m-%d %H:%M:%S')}
      <br>
      % if user.updated_at:
        ${_("Updated at")}: ${user.updated_at.strftime('%Y-%m-%d %H:%M:%S')}
      % endif
    </p>
  </div>
</div>