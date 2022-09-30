<%inherit file="layout.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="card">
  <div class="card-body">
    ${dropdown.filter_button('user_watched', status, filter=filter, sort=sort, order=order, username=user.name)}
    ${dropdown.sort_button('user_watched', dropdown_sort, filter=filter, sort=sort, order=order, username=user.name)}
    ${dropdown.order_button('user_watched', dropdown_order, filter=filter, sort=sort, order=order, username=user.name)}
    <div class="float-end">
      ${button.export('user_watched_export', username=user.name, _query={'filter': filter, 'sort': sort, 'order': order})}
      ${button.clear('user_watched_clear', username=user.name)}
    </div>
  </div>
</div>

<%include file="project_table.mako"/>