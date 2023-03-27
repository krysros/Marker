<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="nav_pills" file="nav_pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${nav_pills.tag_pill(tag)}</div>
  <div>${button.edit('tag_edit', tag_id=tag.id, slug=tag.slug)}</div>
  <div>${button.delete('tag_delete', tag_id=tag.id, slug=tag.slug)}</div>
</div>

<%include file="tag_lead.mako"/>

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