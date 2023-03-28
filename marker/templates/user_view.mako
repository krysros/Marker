<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.user_pill(user)}</div>
  <div>${button.edit('user_edit', username=user.name)}</div>
  <div>${button.delete('user_delete', username=user.name)}</div>
</div>

<p class="lead">${user.fullname}</p>

<div class="card mt-4 mb-4">
  <div class="card-header"><i class="bi bi-person-circle"></i> Użytkownik</div>
  <div class="card-body">
    <dl>
      <dt>Nazwa</dt>
      <dd>${user.name}</dd>

      <dt>Imię i nazwisko</dt>
      <dd>${user.fullname or "---"}</dd>

      <dt>Email</dt>
      % if user.email:
      <dd><a href="mailto:${user.email}">${user.email}</a></dd>
      % else:
      <dd>---</dd>
      % endif

      <dt>Rola</dt>
      <dd>${user.role or "---"}</dd>
    </dl>
  </div>
</div>

<div class="card mt-4 mb-4">
  <div class="card-header"><i class="bi bi-clock"></i> Data modyfikacji</div>
  <div class="card-body">
    <p>
      Utworzono: ${user.created_at.strftime('%Y-%m-%d %H:%M:%S')}
      <br>
      % if user.updated_at:
        Zmodyfikowano: ${user.updated_at.strftime('%Y-%m-%d %H:%M:%S')}
      % endif
    </p>
  </div>
</div>