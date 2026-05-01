<%inherit file="layout.mako"/>

<%
  from marker.forms.select import select_subdivisions
  subdivisions = dict(select_subdivisions(form.country.data))
%>

<div class="card mt-4 mb-4">
  <div class="card-header">${heading}</div>
  <div class="card-body">
    <form action="${context.get('form_action', request.current_route_path())}" method="post">
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
        <!-- pole object_category przeniesione niżej -->
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
          % if gemini_api_key_set:
          <button
            type="button"
            class="btn btn-outline-secondary"
            data-website-autofill-trigger="1"
            title="${_('Refresh form from website')}"
            aria-label="${_('Refresh form from website')}"
          >
            <span data-website-autofill-icon>
              <i class="bi bi-robot"></i>
            </span>
            <span class="spinner-grow spinner-grow-sm d-none" data-website-autofill-spinner role="status" aria-hidden="true"></span>
          </button>
          % endif
        </div>
        % if gemini_api_key_set:
        <div class="form-text">${_("Click the refresh button to fill the remaining fields from the website address.")}</div>
        % endif
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
        ${form.color.label(class_="form-label")}
        ${form.color(class_="form-control" + (" is-invalid" if form.errors.get("color") else ""))}
        % for error in form.errors.get("color", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>
      % if hasattr(form, 'deadline') and form.deadline.type != 'HiddenField':
      <div class="mb-3">
        ${form.deadline.label(class_="form-label")}
        ${form.deadline(class_="form-control" + (" is-invalid" if form.errors.get("deadline") else ""))}
        % for error in form.errors.get("deadline", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>
      % endif
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
      % if hasattr(form, 'object_category'):
      <div class="mb-3">
        ${form.object_category.label(class_="form-label")}
        ${form.object_category(class_="form-control" + (" is-invalid" if form.errors.get("object_category") else ""))}
        % for error in form.errors.get("object_category", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>
      % endif
      % if hasattr(form, 'deadline_from'):
      <div class="row mb-3">
        <div class="col">
          ${form.deadline_from.label(class_="form-label")}
          ${form.deadline_from(class_="form-control")}
        </div>
        <div class="col">
          ${form.deadline_to.label(class_="form-label")}
          ${form.deadline_to(class_="form-control")}
        </div>
      </div>
      % endif
      % if hasattr(form, 'usable_area'):
      <div class="mb-3">
        ${form.usable_area.label(class_="form-label")}
        ${form.usable_area(class_="form-control" + (" is-invalid" if form.errors.get("usable_area") else ""))}
        % for error in form.errors.get("usable_area", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>
      % endif
      % if hasattr(form, 'usable_area_from'):
      <div class="row mb-3">
        <div class="col">
          ${form.usable_area_from.label(class_="form-label")}
          ${form.usable_area_from(class_="form-control")}
        </div>
        <div class="col">
          ${form.usable_area_to.label(class_="form-label")}
          ${form.usable_area_to(class_="form-control")}
        </div>
      </div>
      % endif
      % if hasattr(form, 'cubic_volume'):
      <div class="mb-3">
        ${form.cubic_volume.label(class_="form-label")}
        ${form.cubic_volume(class_="form-control" + (" is-invalid" if form.errors.get("cubic_volume") else ""))}
        % for error in form.errors.get("cubic_volume", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>
      % endif
      % if hasattr(form, 'cubic_volume_from'):
      <div class="row mb-3">
        <div class="col">
          ${form.cubic_volume_from.label(class_="form-label")}
          ${form.cubic_volume_from(class_="form-control")}
        </div>
        <div class="col">
          ${form.cubic_volume_to.label(class_="form-label")}
          ${form.cubic_volume_to(class_="form-control")}
        </div>
      </div>
      % endif
      % if hasattr(form, 'currency'):
      <div class="mb-3">
        ${form.currency.label(class_="form-label")}
        ${form.currency(class_="form-control" + (" is-invalid" if form.errors.get("currency") else ""))}
        % for error in form.errors.get("currency", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>
      % endif
      % if hasattr(form, 'value_net'):
      <div class="mb-3">
        ${form.value_net.label(class_="form-label")}
        ${form.value_net(class_="form-control" + (" is-invalid" if form.errors.get("value_net") else ""))}
        % for error in form.errors.get("value_net", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>
      % endif
      % if hasattr(form, 'value_net_from'):
      <div class="row mb-3">
        <div class="col">
          ${form.value_net_from.label(class_="form-label")}
          ${form.value_net_from(class_="form-control")}
        </div>
        <div class="col">
          ${form.value_net_to.label(class_="form-label")}
          ${form.value_net_to(class_="form-control")}
        </div>
      </div>
      % endif
      % if hasattr(form, 'value_gross'):
      <div class="mb-3">
        ${form.value_gross.label(class_="form-label")}
        ${form.value_gross(class_="form-control" + (" is-invalid" if form.errors.get("value_gross") else ""))}
        % for error in form.errors.get("value_gross", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>
      % endif
      % if hasattr(form, 'value_gross_from'):
      <div class="row mb-3">
        <div class="col">
          ${form.value_gross_from.label(class_="form-label")}
          ${form.value_gross_from(class_="form-control")}
        </div>
        <div class="col">
          ${form.value_gross_to.label(class_="form-label")}
          ${form.value_gross_to(class_="form-control")}
        </div>
      </div>
      % endif
      <div class="mb-3">
        <button type="submit" class="btn btn-primary">${_("Submit")}</button>
      </div>
    </form>
  </div>
</div>