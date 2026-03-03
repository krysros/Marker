<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-people"></i> ${_("Contacts")}
  <span class="badge bg-secondary"><div hx-get="${request.route_url('contact_count')}" hx-trigger="contactEvent from:body">${counter}</div></span>
  <div class="float-end">
    ${button.a(icon='search', color='primary', url=request.route_url('contact_search'))}
    ${button.a(icon='upload', color='success', url=request.route_url('contact_import_csv'))}
  </div>
</h2>

<hr>

<div class="alert alert-info" role="alert">
  <strong>${_("Tags")}: </strong>
  % for tag in tags:
    <span class="badge bg-secondary">${tag}</span>
  % endfor
</div>

<%include file="contact_tags_table.mako"/>
