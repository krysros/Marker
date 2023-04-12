<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="user_pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.pills(user)}</div>
  <div>${button.a_btn(icon='pencil-square', color='warning', url=request.route_url('user_edit', username=user.name))}</div>
  <div>${button.button(icon='trash', color='danger', url=request.route_url('user_delete', username=user.name))}</div>
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