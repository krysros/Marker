<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<%!
  import pycountry
%>

<h2>
  <i class="bi bi-briefcase"></i> ${_("Projects")}
  <span class="badge bg-secondary"><div hx-get="${request.route_url('project_count')}" hx-trigger="projectEvent from:body">${counter}</div></span>
  <div class="float-end">
    ${button.a_btn(icon='map', color='secondary', url=request.route_url('project_map', _query=search_query))}
    ${button.a_btn(icon='search', color='primary', url=request.route_url('project_search'))}
    ${button.a_btn(icon='plus-lg', color='success', url=request.route_url('project_add'))}
  </div>
</h2>

<hr>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown(dd_filter, search_query)}</div>
  <div>${button.dropdown(dd_sort, search_query)}</div>
  <div>${button.dropdown(dd_order, search_query)}</div>
</div>

% if any(x for x in form.data.values() if x):
<div class="alert alert-info" role="alert">
  <strong>${_("Search criteria")}: </strong> 
  % for k, v in form.data.items():
    % if v:
      % if k == "color":
        ${form[k].label.text}: <strong>${colors.get(v)}</strong>;
      % elif k == "subdivision":
        ${form[k].label.text}: <strong>${getattr(pycountry.subdivisions.get(code=v), "name", "---")}</strong>;
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