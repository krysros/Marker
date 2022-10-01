<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="card">
  <div class="card-header">
    <div class="row">
      <div class="col-10">
        <ul class="nav nav-tabs card-header-tabs">
          <li class="nav-item">
            <a class="nav-link active" aria-current="page" href="${request.route_url('tag_view', tag_id=tag.id, slug=tag.slug)}">Tag</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="${request.route_url('tag_companies', tag_id=tag.id, slug=tag.slug)}">Firmy</a>
          </li>
        </ul>
      </div>
      <div class="col-2">
        <div class="float-end">
          ${button.edit('tag_edit', tag_id=tag.id, slug=tag.slug)}
          ${button.delete('tag_delete', tag_id=tag.id, slug=tag.slug)}    
        </div>
      </div>
    </div>
  </div>
  <div class="card-body">
    <dl>
      <dt>Nazwa tagu</dt>
      <dd>${tag.name}</dd>
    </dl>
  </div>
</div>

<div class="card">
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