<%include file="navbar.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="card">
  <div class="card-body">
    <div class="float-end">
      <button hx-post="${request.route_url('project_watch', project_id=project.id)}" hx-target="#watch" class="btn btn-primary">
        <div id="watch">
        % if project in request.identity.watched:
          <i class="bi bi-eye-fill"></i>
        % else:
          <i class="bi bi-eye"></i>
        % endif
        </div>
      </button>
      ${button.edit('project_edit', project_id=project.id, slug=project.slug)}
      ${button.danger('project_delete', 'Usuń', project_id=project.id, slug=project.slug)}
    </div>
  </div>
</div>

<div class="card">
  <div class="card-header"><i class="bi bi-briefcase"></i> Projekt</div>
  <div class="card-body">
    <div class="row">
      <div class="col">
        <h1>${project.name}</h1>
      </div>
    </div>
    <div class="row">
      <div class="col">
        <dl class="dl-horizontal">
          <dt>Adres</dt>
          <dd>
            ${project.street}<br>
            % if project.postcode:
            ${project.postcode} ${project.city}<br>
            % else:
            ${project.city}<br>
            % endif
            ${states.get(project.state)}<br>
          </dd>
          <dt>Termin</dt>
          % if project.deadline:
          <dd>${project.deadline}</dd>
          % else:
          <dd>---</dd>
          % endif
          <dt>Link</dt>
          <dd><a href="${project.link}" target="_blank">${project.link}</a></dd>
        </dl>
      </div>
    </div>
  </div>
  <div class="card-footer">
    <ul class="nav">
##      <li class="nav-item">
##        <a class="nav-link" role="button" href="#" hx-get="${request.route_url('project_comments', project_id=project.id, slug=project.slug)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">
##        % if c_comments > 0:
##        Komentarze <span class="badge text-bg-warning">${c_comments}</span>
##        % else:
##        Komentarze <span class="badge text-bg-secondary">0</span>
##        % endif
##        </a>
##      </li>
      <li class="nav-item">
        <a class="nav-link" role="button" href="#" hx-get="${request.route_url('project_watched', project_id=project.id, slug=project.slug)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">
          % if c_watched > 0:
          Obserwacje <span class="badge text-bg-success">${c_watched}</span></a>
          % else:
          Obserwacje <span class="badge text-bg-secondary">0</span></a>
          % endif
      </li>
      <li class="nav-item">
        <a class="nav-link" role="button" href="#" hx-get="${request.route_url('project_companies', project_id=project.id, slug=project.slug)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">
          % if c_companies > 0:
          Firmy <span class="badge text-bg-info">${c_companies}</span>
          % else:
          Firmy <span class="badge text-bg-secondary">0</span>
          % endif
        </a>
      </li>
##      <li class="nav-item">
##        <a class="nav-link" role="button" href="#" hx-get="${request.route_url('project_similar', project_id=project.id, slug=project.slug)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">
##          % if c_similar > 0:
##          Podobne <span class="badge text-bg-dark">${c_simiar}</span></a>
##          % else:
##          Podobne <span class="badge text-bg-secondary">0</span></a>
##          % endif
##        </a>
##      </li>
    </ul>
  </div>
</div>

<div class="card">
  <div class="card-header"><i class="bi bi-clock"></i> Data modyfikacji</div>
  <div class="card-body">
    <p>
      Utworzono: ${project.created_at.strftime('%Y-%m-%d %H:%M:%S')}
      % if project.created_by:
        przez <a href="#" hx-get="${request.route_url('user_view', username=project.created_by.name, what='info')}" hx-target="#main-container" hx-swap="innerHTML show:window:top">${project.created_by.name}</a>
      % endif
      <br>
      % if project.updated_at:
        Zmodyfikowano: ${project.updated_at.strftime('%Y-%m-%d %H:%M:%S')}
        % if project.updated_by:
          przez <a href="#" hx-get="${request.route_url('user_view', username=project.updated_by.name, what='info')}" hx-target="#main-container" hx-swap="innerHTML show:window:top">${project.updated_by.name}</a>
        % endif
      % endif
    </p>
  </div>
</div>