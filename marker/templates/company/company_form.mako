<%inherit file="layout.mako"/>

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
        ${form.website(class_="form-control" + (" is-invalid" if form.errors.get("website") else ""))}
        % for error in form.errors.get("website", []):
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
      <div class="mb-3">
        ${form.NIP.label(class_="form-label")}
        ${form.NIP(class_="form-control" + (" is-invalid" if form.errors.get("NIP") else ""))}
        % for error in form.errors.get("NIP", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>
      <div class="mb-3">
        ${form.REGON.label(class_="form-label")}
        ${form.REGON(class_="form-control" + (" is-invalid" if form.errors.get("REGON") else ""))}
        % for error in form.errors.get("REGON", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>
      <div class="mb-3">
        ${form.KRS.label(class_="form-label")}
        ${form.KRS(class_="form-control" + (" is-invalid" if form.errors.get("KRS") else ""))}
        % for error in form.errors.get("KRS", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>
      <div class="mb-3">
        ${form.court.label(class_="form-label")}
        ${form.court(class_="form-control" + (" is-invalid" if form.errors.get("court") else ""))}
        % for error in form.errors.get("court", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>
      <div class="mb-3">
        <button type="submit" class="btn btn-primary">${_("Submit")}</button>
      </div>
    </form>
  </div>
</div>