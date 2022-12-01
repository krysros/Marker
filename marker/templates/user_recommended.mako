<%inherit file="layout.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>
<%namespace name="button" file="button.mako"/>

<h2><i class="bi bi-hand-thumbs-up"></i> Rekomendowane
  <div class="float-end">
    ${button.export('user_recommended_export', username=user.name, _query={'filter': filter, 'sort': sort, 'order': order})}
    ${button.clear_recommended('user_recommended_clear', username=user.name)}
  </div>
</h2>
<hr>

<div class="card border-0">
  <div class="row">
    <div class="col">
      ${dropdown.sort_button('user_recommended', dropdown_sort, username=user.name)}
      ${dropdown.order_button('user_recommended', dropdown_order, username=user.name)}
    </div>
  </div>
</div>

<%include file="company_table.mako"/>
