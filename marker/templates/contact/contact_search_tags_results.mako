<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-people"></i> ${_("Contacts")}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.a(icon='arrow-left', color='secondary', url=request.route_url('contact_search_tags', _query={'tag': tags}))}
    ${button.a(icon='folder', color='secondary', url=request.route_url('contact_all'))}
    ${button.a(icon='search', color='primary', url=request.route_url('contact_search'))}
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
