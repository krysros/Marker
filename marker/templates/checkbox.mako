<%def name="check_company(company)">
% if company in request.identity.selected_companies:
<input class="form-check-input"
       type="checkbox"
       value="${company.id}"
       autocomplete="off"
       checked
       hx-post="${request.route_url('company_check', company_id=company.id)}"
       hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
       hx-trigger="click"
       hx-swap="none">
% else:
<input class="form-check-input"
       type="checkbox"
       value="${company.id}"
       autocomplete="off"
       hx-post="${request.route_url('company_check', company_id=company.id)}"
       hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
       hx-trigger="click"
       hx-swap="none">
% endif
</%def>

<%def name="check_project(project)">
% if project in request.identity.selected_projects:
<input class="form-check-input"
      type="checkbox"
      value="${project.id}"
      autocomplete="off"
      checked
      hx-post="${request.route_url('project_check', project_id=project.id)}"
      hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
      hx-trigger="click"
      hx-swap="none">
% else:
<input class="form-check-input"
      type="checkbox"
      value="${project.id}"
      autocomplete="off"
      hx-post="${request.route_url('project_check', project_id=project.id)}"
      hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
      hx-trigger="click"
      hx-swap="none">
% endif
</%def>

<%def name="check_tag(tag)">
% if tag in request.identity.selected_tags:
<input class="form-check-input"
      type="checkbox"
      value="${tag.id}"
      autocomplete="off"
      checked
      hx-post="${request.route_url('tag_check', tag_id=tag.id)}"
      hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
      hx-trigger="click"
      hx-swap="none">
% else:
<input class="form-check-input"
      type="checkbox"
      value="${tag.id}"
      autocomplete="off"
      hx-post="${request.route_url('tag_check', tag_id=tag.id)}"
      hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
      hx-trigger="click"
      hx-swap="none">
% endif
</%def>

<%def name="check_contact(contact)">
% if contact in request.identity.selected_contacts:
<input class="form-check-input"
      type="checkbox"
      value="${contact.id}"
      autocomplete="off"
      checked
      hx-post="${request.route_url('contact_check', contact_id=contact.id)}"
      hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
      hx-trigger="click"
      hx-swap="none">
% else:
<input class="form-check-input"
      type="checkbox"
      value="${contact.id}"
      autocomplete="off"
      hx-post="${request.route_url('contact_check', contact_id=contact.id)}"
      hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
      hx-trigger="click"
      hx-swap="none">
% endif
</%def>