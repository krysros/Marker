<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-hand-thumbs-up"></i> ${_("Recommended")}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.button(icon='hand-thumbs-up', color='warning', url=request.route_url('user_clear_recommended', username=user.name))}
  </div>
</h2>
<hr>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown(dd_filter)}</div>
  <div>${button.dropdown(dd_sort)}</div>
  <div class="me-auto">${button.dropdown(dd_order)}</div>
  <div>${button.a_btn(icon='download', color='primary', url=request.route_url('user_export_recommended', username=user.name, _query={'filter': dd_filter._filter, 'sort': dd_sort._sort, 'order': dd_order._order}))}</div>
</div>

<%include file="company_table.mako"/>
