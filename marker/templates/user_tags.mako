<%inherit file="layout.mako"/>

<div class="card border-0">
  <div class="row">
    <div class="col">
      <ul class="nav nav-pills">
        <li class="nav-item">
          <a class="nav-link" href="${request.route_url('user_view', username=user.name)}">Użytkownik</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="${request.route_url('user_companies', username=user.name)}">Firmy</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="${request.route_url('user_projects', username=user.name)}">Projekty</a>
        </li>
        <li class="nav-item">
          <a class="nav-link active" aria-current="page" href="${request.route_url('user_tags', username=user.name)}">Tagi</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="${request.route_url('user_persons', username=user.name)}">Osoby</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="${request.route_url('user_comments', username=user.name)}">Komentarze</a>
        </li>
      </ul>
    </div>
  </div>
</div>

<%include file="tag_table.mako"/>