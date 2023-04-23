<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<%!
  import pycountry
%>

<h2>
  <i class="bi bi-buildings"></i> ${_("Companies")}
  <span class="badge bg-secondary"><div hx-get="${request.route_url('company_count')}" hx-trigger="companyEvent from:body">${counter}</div></span>
  <div class="float-end">
    ${button.a_button(icon='map', color='secondary', url=request.route_url('company_map', _query=search_query))}
    ${button.a_button(icon='search', color='primary', url=request.route_url('company_search'))}
    ${button.a_button(icon='plus-lg', color='success', url=request.route_url('company_add'))}
  </div>
</h2>

<hr>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown(dd_sort)}</div>
  <div>${button.dropdown(dd_order)}</div>
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
      % else:
        ${form[k].label.text}: <strong>${v}</strong>;
      % endif
    % endif
  % endfor
</div>
% endif

<%include file="company_table.mako"/>