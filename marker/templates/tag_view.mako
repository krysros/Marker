<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">
    <ul class="nav nav-pills">
      <li class="nav-item">
        <a class="nav-link active" aria-current="page" href="${request.route_url('tag_view', tag_id=tag.id, slug=tag.slug)}">Tag</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('tag_companies', tag_id=tag.id, slug=tag.slug)}">
          Firmy <span class="badge text-bg-secondary">${c_companies}</span>
        </a>
      </li>
    </ul>
  </div>
  <div>${button.edit('tag_edit', tag_id=tag.id, slug=tag.slug)}</div>
  <div>${button.delete('tag_delete', tag_id=tag.id, slug=tag.slug)}</div>
</div>

<p class="lead">${tag.name}</p>

<div class="card mt-4 mb-4">
  <div class="card-header"><i class="bi bi-tag"></i> Tag</div>
  <div class="card-body">
    <div class="row">
      <div class="col">
        <dl>
          <dt>Nazwa</dt>
          <dd>${tag.name}</dd>
        </dl>
      </div>
    </div>
  </div>
</div>

<div class="card mt-4 mb-4">
  <div class="card-header"><i class="bi bi-clock"></i> Data modyfikacji</div>
  <div class="card-body">
    <p>
      Utworzono: ${tag.created_at.strftime('%Y-%m-%d %H:%M:%S')}
      % if tag.created_by:
        przez <a href="${request.route_url('user_view', username=tag.created_by.name)}">${tag.created_by.name}</a>
      % endif
      <br>
      % if tag.updated_at:
        Zmodyfikowano: ${tag.updated_at.strftime('%Y-%m-%d %H:%M:%S')}
        % if tag.updated_by:
          przez <a href="${request.route_url('user_view', username=tag.updated_by.name)}">${tag.updated_by.name}</a>
        % endif
      % endif
    </p>
  </div>
</div>