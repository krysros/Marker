<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-person-circle"></i> Użytkownicy
  <small class="text-muted">${heading}</small>
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

<%include file="user_table.mako"/>