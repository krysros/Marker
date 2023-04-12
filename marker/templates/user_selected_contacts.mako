<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-check-square"></i> ${_("Contacts")}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.clear('user_clear_selected_contacts', icon='square', username=user.name)}
  </div>
</h2>
<hr>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown('user_selected_contacts', dd_sort, username=user.name)}</div>
  <div class="me-auto">${button.dropdown('user_selected_contacts', dd_order, username=user.name)}</div>
  <div>${button.button('user_export_selected_contacts', color='primary', icon='download', username=user.name, _query={'sort': dd_sort._sort, 'order': dd_order._order})}</div>
</div>

<%include file="contact_table.mako"/>