<%inherit file="layout.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="card border-0">
  <div class="row">
    <div class="col">
      ${dropdown.sort_button('user_recomended', dropdown_sort, username=user.name)}
      ${dropdown.order_button('user_recomended', dropdown_order, username=user.name)}
      <div class="float-end">
        ${button.export('user_recomended_export', username=user.name, _query={'filter': filter, 'sort': sort, 'order': order})}
        ${button.clear('user_recomended_clear', username=user.name)}
      </div>
    </div>
  </div>
</div>

<%include file="company_table.mako"/>
