<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-tags"></i> ${_("Tags")}
  <span class="badge bg-secondary"><div hx-get="${request.route_url('tag_count')}" hx-trigger="tagEvent from:body">${counter}</div></span>
  <div class="float-end">
    ${button.a_button(icon='search', color='primary', url=request.route_url('tag_search'))}
    ${button.a_button(icon='plus-lg', color='success', url=request.route_url('tag_add'))}
  </div>
</h2>
<hr>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown(dd_sort)}</div>
  <div>${button.dropdown(dd_order)}</div>
</div>

% if any(x for x in search_query.values() if x):
<div class="alert alert-info" role="alert">
  <strong>${_("Search criteria")}: </strong>
  % for k, v in search_query.items():
    ${k}:
    % if isinstance(v, list):
      <strong>${", ".join(v)}</strong>;
    % else:
      <strong>${v}</strong>;
    % endif
  % endfor
</div>
% endif

<%include file="tag_table.mako"/>