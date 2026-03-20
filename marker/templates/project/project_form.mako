<%inherit file="layout.mako"/>

<%
  from marker.forms.select import select_subdivisions
  subdivisions = dict(select_subdivisions(form.country.data))
%>

<div class="card mt-4 mb-4">
  <div class="card-header">${heading}</div>
  <div class="card-body">
    <form action="${request.current_route_path()}" method="post">
      <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
      <div class="mb-3">
        ${form.name.label(class_="form-label")}
        ${form.name(class_="form-control" + (" is-invalid" if form.errors.get("name") else ""))}
        % for error in form.errors.get("name", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>
      <div class="mb-3">
        ${form.street.label(class_="form-label")}
        ${form.street(class_="form-control" + (" is-invalid" if form.errors.get("street") else ""))}
        % for error in form.errors.get("street", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>
      <div class="mb-3">
        ${form.postcode.label(class_="form-label")}
        ${form.postcode(class_="form-control" + (" is-invalid" if form.errors.get("postcode") else ""))}
        % for error in form.errors.get("postcode", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>
      <div class="mb-3">
        ${form.city.label(class_="form-label")}
        ${form.city(class_="form-control" + (" is-invalid" if form.errors.get("city") else ""))}
        % for error in form.errors.get("city", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>
      <div class="mb-3">
        ${form.country.label(class_="form-label")}
        ${form.country(class_="form-control" + (" is-invalid" if form.errors.get("country") else ""), **{"hx-get": f"{request.route_url('subdivision')}", "hx-target": "#subdivision"})}
        % for error in form.errors.get("country", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>
      <div class="mb-3">
        ${form.subdivision.label(class_="form-label")}
        <select class="form-control" id="subdivision" name="subdivision">
        % for code, name in subdivisions.items():
          % if form.subdivision.data == code:
            <option value="${code}" selected>${name}</option>
          % else:
            <option value="${code}">${name}</option>
          % endif
        % endfor
        </select>
        % for error in form.errors.get("subdivision", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>
      <div class="mb-3">
        ${form.website.label(class_="form-label")}
        <div class="input-group">
          ${form.website(
            class_="form-control" + (" is-invalid" if form.errors.get("website") else ""),
            **{
              "data-website-autofill-url": request.route_url("project_website_autofill"),
              "data-subdivision-url": request.route_url("subdivision"),
            }
          )}
          <button
            type="button"
            class="btn btn-outline-secondary"
            data-website-autofill-trigger="1"
            title="${_('Refresh form from website')}"
            aria-label="${_('Refresh form from website')}"
          >
            <i class="bi bi-arrow-clockwise"></i>
          </button>
        </div>
        <div class="form-text">${_("Click the refresh button to fill the remaining fields from the website address.")}</div>
        % for error in form.errors.get("website", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
        % for error in form.errors.get("website", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
        % if hasattr(form, 'shorten_website'):
          <div class="form-check mt-2">
            ${form.shorten_website(class_="form-check-input")}
            <label class="form-check-label" for="shorten_website">
              ${form.shorten_website.label(class_="form-label")}
            </label>
          </div>
        % endif
      </div>
      <div class="mb-3">
        ${form.deadline.label(class_="form-label")}
        ${form.deadline(class_="form-control" + (" is-invalid" if form.errors.get("deadline") else ""))}
        % for error in form.errors.get("deadline", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>
      <div class="mb-3">
        ${form.stage.label(class_="form-label")}
        ${form.stage(class_="form-control" + (" is-invalid" if form.errors.get("stage") else ""))}
        % for error in form.errors.get("stage", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>
      <div class="mb-3">
        ${form.delivery_method.label(class_="form-label")}
        ${form.delivery_method(class_="form-control" + (" is-invalid" if form.errors.get("delivery_method") else ""))}
        % for error in form.errors.get("delivery_method", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>
      <div class="mb-3">
        ${form.color.label(class_="form-label")}
        ${form.color(class_="form-control" + (" is-invalid" if form.errors.get("color") else ""))}
        % for error in form.errors.get("color", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>
      % if request.matched_route.name in ("project_add", "project_search"):
      <% tag_input_route = 'project_search_tag_input' if request.matched_route.name == 'project_search' else 'project_add_tag_input' %>
      <% tag_remove_route = 'project_search_tag_input_remove' if request.matched_route.name == 'project_search' else 'project_add_tag_input_remove' %>
      <div class="mb-3">
        <label class="form-label">${_("Tags")}</label>
        <div id="project-tag-inputs" class="vstack gap-2">
          % if tags:
            % for index, value in enumerate(tags, start=1):
              <%include file="project_tag_input_row.mako" args="row_id='project-tag-' + str(index), value=value, remove_route=tag_remove_route"/>
            % endfor
          % else:
            <%include file="project_tag_input_row.mako" args="row_id='project-tag-1', value='', remove_route=tag_remove_route"/>
          % endif
        </div>
        <button type="button"
                class="btn btn-outline-secondary btn-sm mt-2"
                title="${_('Tag')}"
                aria-label="${_('Tag')}"
                hx-get="${request.route_url(tag_input_route)}"
                hx-target="#project-tag-inputs"
                hx-swap="beforeend">
          <i class="bi bi-plus-lg me-1"></i>${_('Tag')}
        </button>
      </div>
      % endif
      <div class="mb-3">
        <button type="submit" class="btn btn-primary">${_("Submit")}</button>
      </div>
    </form>
  </div>
</div>