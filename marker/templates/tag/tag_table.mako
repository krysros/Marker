<%namespace name="button" file="button.mako"/>
<%namespace name="checkbox" file="checkbox.mako"/>

<%def name="rows()">
<%
  category = q.get("category") if q else None
  show_companies = category != "projects"
  show_projects = category != "companies"
%>
% for tag in paginator:
% if loop.last:
<tr hx-get="${next_page}"
    hx-trigger="revealed"
    hx-swap="afterend">
% else:
<tr>
% endif
  <td>${checkbox.checkbox(tag, selected_ids=selected_ids('selected_tags'), url=request.route_url('tag_check', tag_id=tag.id, slug=tag.slug))}</td>
  <td>
    <a href="${request.route_url('tag_view', tag_id=tag.id, slug=tag.slug)}">${tag.name}</a><br>
    <small class="text-body-secondary">${_("Created at")}: ${tag.created_at.strftime('%Y-%m-%d %H:%M:%S')}</small><br>
    <small class="text-body-secondary">${_("Updated at")}: ${tag.updated_at.strftime('%Y-%m-%d %H:%M:%S')}</small>
  </td>
  % if show_companies:
  <td>
    <a href="${request.route_url('tag_companies', tag_id=tag.id, slug=tag.slug)}">
      <span class="badge text-bg-secondary" role="button">${tag.count_companies}</span>
    </a>
  </td>
  % endif
  % if show_projects:
  <td>
    <a href="${request.route_url('tag_projects', tag_id=tag.id, slug=tag.slug)}">
      <span class="badge text-bg-secondary" role="button">${tag.count_projects}</span>
    </a>
  </td>
  % endif
  <td>
    <div class="hstack gap-2 mx-2">
      ${button.a(icon='pencil-square', color='warning', size='sm', url=request.route_url('tag_edit', tag_id=tag.id, slug=tag.slug))}
      ${button.del_row(icon='trash', color='danger', size='sm', url=request.route_url('tag_del_row', tag_id=tag.id, slug=tag.slug))}
    </div>
  </td>
</tr>
% endfor
</%def>

<%
  category = q.get("category") if q else None
  show_companies = category != "projects"
  show_projects = category != "companies"
%>

<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th>${checkbox.select_all()}</th>
        <th>${_("Tag")}</th>
        % if show_companies:
        <th>${_("Companies")}</th>
        % endif
        % if show_projects:
        <th>${_("Projects")}</th>
        % endif
        <th>${_("Action")}</th>
      </tr>
    </thead>
    <tbody>
      ${rows()}
    </tbody>
  </table>
</div>