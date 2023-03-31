<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-briefcase"></i> ${_("Projects")}
  <span class="badge bg-secondary"><div hx-get="${request.route_url('project_count')}" hx-trigger="projectEvent from:body">${counter}</div></span>
  <div class="float-end">
    ${button.map('project_map', _query=search_query)}
    ${button.search('project_search')}
    ${button.add('project_add')}
  </div>
</h2>

<hr>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown('project_all', dd_filter)}</div>
  <div>${button.dropdown('project_all', dd_sort)}</div>
  <div>${button.dropdown('project_all', dd_order)}</div>
</div>

% if any(x for x in form.data.values() if x):
<div class="alert alert-info" role="alert">
  <strong>${_("Search criteria")}: </strong> 
  % for k, v in form.data.items():
    % if v:
      % if k == "color":
        ${form[k].label.text}: <strong>${colors.get(v)}</strong>;
      % elif k == "region":
        ${form[k].label.text}: <strong>${regions.get(v)}</strong>;
      % elif k == "country":
        ${form[k].label.text}: <strong>${countries.get(v)}</strong>;
      % elif k == "stages":
        ${form[k].label.text}: <strong>${stages.get(v)}</strong>;
      % elif k == "delivery_method":
        ${form[k].label.text}: <strong>${project_delivery_methods.get(v)}</strong>;
      % else:
        ${form[k].label.text}: <strong>${v}</strong>;
      % endif
    % endif
  % endfor
</div>
% endif

<%include file="project_table.mako"/>