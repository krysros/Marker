<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-eye"></i> Obserwowane
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.clear('user_watched_clear', icon='eye', username=user.name)}
  </div>
</h2>
<hr>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown('user_watched', items=status, criterion=filter, typ='filter', title='Filtruj', username=user.name)}</div>
  <div>${button.dropdown('user_watched', items=dropdown_sort, criterion=sort, typ='sort', title='Sortuj', username=user.name)}</div>
  <div class="me-auto">${button.dropdown('user_watched', items=dropdown_order, criterion=order, typ='order', title='Kolejność', username=user.name)}</div>
  <div>${button.export('user_watched_export', username=user.name, _query={'filter': filter, 'sort': sort, 'order': order})}</div>
</div>

<%include file="project_table.mako"/>