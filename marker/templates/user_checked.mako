<%inherit file="layout.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="card">
  <div class="card-body">
    ${dropdown.sort_button('user_checked', dropdown_sort, username=user.name)}
    ${dropdown.order_button('user_checked', dropdown_order, username=user.name)}
    <div class="float-end">
      ${button.export('user_checked_export', username=user.name, _query={'filter': filter, 'sort': sort, 'order': order})}
      ${button.clear('user_checked_clear', username=user.name)}
    </div>
  </div>
</div>

<%include file="company_table.mako"/>