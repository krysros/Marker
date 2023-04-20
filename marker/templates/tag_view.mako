<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.pills(tag_pills)}</div>
  <div>${button.a_btn(icon='pencil-square', color='warning', url=request.route_url('tag_edit', tag_id=tag.id, slug=tag.slug))}</div>
  <div>${button.button(icon='trash', color='danger', url=request.route_url('tag_delete', tag_id=tag.id, slug=tag.slug))}</div>
</div>

<%include file="tag_lead.mako"/>

<div class="card mt-4 mb-4">
  <div class="card-header"><i class="bi bi-tag"></i> ${_("Tag")}</div>
  <div class="card-body">
    <div class="row">
      <div class="col">
        <dl>
          <dt>${_("Name")}</dt>
          <dd>${tag.name}</dd>
        </dl>
      </div>
    </div>
  </div>
</div>

<div class="card mt-4 mb-4">
  <div class="card-header"><i class="bi bi-clock"></i> ${_("Modification date")}</div>
  <div class="card-body">
    <p>
      ${_("Created at")}: ${tag.created_at.strftime('%Y-%m-%d %H:%M:%S')}
      % if tag.created_by:
        ${_("by")} <a href="${request.route_url('user_view', username=tag.created_by.name)}">${tag.created_by.name}</a>
      % endif
      <br>
      % if tag.updated_at:
        ${_("Updated at")}: ${tag.updated_at.strftime('%Y-%m-%d %H:%M:%S')}
        % if tag.updated_by:
          ${_("by")} <a href="${request.route_url('user_view', username=tag.updated_by.name)}">${tag.updated_by.name}</a>
        % endif
      % endif
    </p>
  </div>
</div>