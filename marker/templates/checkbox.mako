<%def name="company(obj)">
% if obj in request.identity.selected_companies:
<input class="form-check-input"
       type="checkbox"
       value="${obj.id}"
       autocomplete="off"
       checked
       hx-post="${request.route_url('company_check', company_id=obj.id, slug=obj.slug)}"
       hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
       hx-trigger="click"
       hx-swap="none">
% else:
<input class="form-check-input"
       type="checkbox"
       value="${obj.id}"
       autocomplete="off"
       hx-post="${request.route_url('company_check', company_id=obj.id, slug=obj.slug)}"
       hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
       hx-trigger="click"
       hx-swap="none">
% endif
</%def>

<%def name="project(obj)">
% if obj in request.identity.selected_projects:
<input class="form-check-input"
      type="checkbox"
      value="${obj.id}"
      autocomplete="off"
      checked
      hx-post="${request.route_url('project_check', project_id=obj.id, slug=obj.slug)}"
      hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
      hx-trigger="click"
      hx-swap="none">
% else:
<input class="form-check-input"
      type="checkbox"
      value="${obj.id}"
      autocomplete="off"
      hx-post="${request.route_url('project_check', project_id=obj.id, slug=obj.slug)}"
      hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
      hx-trigger="click"
      hx-swap="none">
% endif
</%def>

<%def name="tag(obj)">
% if obj in request.identity.selected_tags:
<input class="form-check-input"
      type="checkbox"
      value="${obj.id}"
      autocomplete="off"
      checked
      hx-post="${request.route_url('tag_check', tag_id=obj.id, slug=obj.slug)}"
      hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
      hx-trigger="click"
      hx-swap="none">
% else:
<input class="form-check-input"
      type="checkbox"
      value="${obj.id}"
      autocomplete="off"
      hx-post="${request.route_url('tag_check', tag_id=obj.id, slug=obj.slug)}"
      hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
      hx-trigger="click"
      hx-swap="none">
% endif
</%def>

<%def name="contact(obj)">
% if obj in request.identity.selected_contacts:
<input class="form-check-input"
      type="checkbox"
      value="${obj.id}"
      autocomplete="off"
      checked
      hx-post="${request.route_url('contact_check', contact_id=obj.id, slug=obj.slug)}"
      hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
      hx-trigger="click"
      hx-swap="none">
% else:
<input class="form-check-input"
      type="checkbox"
      value="${obj.id}"
      autocomplete="off"
      hx-post="${request.route_url('contact_check', contact_id=obj.id, slug=obj.slug)}"
      hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
      hx-trigger="click"
      hx-swap="none">
% endif
</%def>