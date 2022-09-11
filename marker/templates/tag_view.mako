<%include file="navbar.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>
<%namespace name="modal" file="modal.mako"/>

<form id="tag_export" action="${request.route_url('tag_export', tag_id=tag.id)}" method="post">
  <input type="hidden" name="csrf_token" value="${request.session.get_csrf_token()}">
  <input type="hidden" name="filter" value=${filter}>
  <input type="hidden" name="sort" value=${sort}>
  <input type="hidden" name="order" value=${order}>
</form>

<div class="card">
  <div class="card-body">
    ${dropdown.filter_button('tag_view', states, filter=filter, sort=sort, order=order, tag_id=tag.id, slug=tag.slug)}
    ${dropdown.sort_button('tag_view', dropdown_sort, filter=filter, sort=sort, order=order, tag_id=tag.id, slug=tag.slug)}
    ${dropdown.order_button('tag_view', dropdown_order, filter=filter, sort=sort, order=order, tag_id=tag.id, slug=tag.slug)}
    <div class="float-end">
      <button type="submit" class="btn btn-primary" form="tag_export" value="submit">Eksportuj</button>
      <a class="btn btn-warning" role="button" href="#" hx-get="${request.route_url('tag_edit', tag_id=tag.id, slug=tag.slug)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">Edytuj</a>
      ${modal.danger_dialog('tag_delete', 'Usuń', 'Czy na pewno chcesz usunąć tag z bazy danych?', tag_id=tag.id, slug=tag.slug)}
    </div>
  </div>
</div>

<%include file="company_table.mako"/>