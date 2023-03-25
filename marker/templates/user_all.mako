<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-person-circle"></i> Użytkownicy
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.search('user_search')}
    ${button.add('user_add')}
  </div>
</h2>

<hr>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown('user_all', dd_filter)}</div>
  <div>${button.dropdown('user_all', dd_sort)}</div>
  <div>${button.dropdown('user_all', dd_order)}</div>
</div>

% if any(x for x in form.data.values() if x):
<div class="alert alert-info" role="alert">
  <strong>Kryteria wyszukiwania: </strong>
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