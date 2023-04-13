<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-person-circle"></i> ${_("Users")}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.a_btn(icon='search', color='primary', url=request.route_url('user_search'))}
    ${button.a_btn(icon='plus-lg', color='success', url=request.route_url('user_add'))}
  </div>
</h2>

<hr>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown(dd_filter, url=request.route_url('user_all'))}</div>
  <div>${button.dropdown(dd_sort, url=request.route_url('user_all'))}</div>
  <div>${button.dropdown(dd_order, url=request.route_url('user_all'))}</div>
</div>

% if any(x for x in form.data.values() if x):
<div class="alert alert-info" role="alert">
  <strong>${_("Search criteria")}: </strong>
  % for k, v in form.data.items():
    % if v:
      % if k == "role":
        ${form[k].label.text}: <strong>${roles.get(v)}</strong>; 
      % else:
        ${form[k].label.text}: <strong>${v}</strong>; 
      % endif
    % endif
  % endfor
</div>
% endif

<%include file="user_table.mako"/>