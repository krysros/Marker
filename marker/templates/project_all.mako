<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-briefcase"></i> Projekty
  <small class="text-muted">${heading}</small>
  <span class="badge bg-secondary">${counter}</span>
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

% if heading:
<div class="alert alert-info" role="alert">
  Kryteria wyszukiwania: 
  % for k, v in form.data.items():
    % if v:
      % if k == "color":
        ${form[k].label.text}: <strong>${colors.get(v)}</strong>;
      % elif k == "state":
        ${form[k].label.text}: <strong>${states.get(v)}</strong>;
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