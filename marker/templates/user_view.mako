<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="card">
  <div class="card-header">
    <ul class="nav nav-tabs card-header-tabs">
      <li class="nav-item">
        <a class="nav-link active" aria-current="page" href="${request.route_url('user_view', username=user.name)}">Użytkownik</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('user_companies', username=user.name)}">Firmy</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('user_projects', username=user.name)}">Projekty</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('user_tags', username=user.name)}">Tagi</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('user_persons', username=user.name)}">Osoby</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('user_comments', username=user.name)}">Komentarze</a>
      </li>
    </ul>
  </div>
  <div class="card-body">
    <div class="d-flex">
      <div class="p-2 flex-fill">
        <dl class="dl-horizontal">
          <dt>Nazwa użytkownika</dt>
          <dd>${user.name}</dd>
    
          <dt>Imię i nazwisko</dt>
          <dd>${user.fullname}</dd>
    
          <dt>Email</dt>
          <dd><a href="mailto:${user.email}">${user.email}</a></dd>
    
          <dt>Rola</dt>
          <dd>${user.role}</dd>
        </dl>
      </div>
      <div class="p-2">
        ${button.edit('user_edit', username=user.name)}
        ${button.danger('user_delete', 'Usuń', username=user.name)}
      </div>
    </div>
  </div>
</div>

<div class="card">
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