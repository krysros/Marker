<%inherit file="layout.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>
<%namespace name="button" file="button.mako"/>

<h2><i class="bi bi-eye"></i> Obserwowane
  <div class="float-end">
    ${button.export('user_watched_export', username=user.name, _query={'filter': filter, 'sort': sort, 'order': order})}
    ${button.clear_watched('user_watched_clear', username=user.name)}
  </div>
</h2>
<hr>

<div class="card border-0">
  <div class="row">
    <div class="col">
      ${dropdown.filter_button('user_watched', status, username=user.name)}
      ${dropdown.sort_button('user_watched', dropdown_sort, username=user.name)}
      ${dropdown.order_button('user_watched', dropdown_order, username=user.name)}
    </div>
  </div>
</div>

<%include file="project_table.mako"/>