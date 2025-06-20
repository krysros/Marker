<%inherit file="layout.mako"/>
<%include file="errors.mako"/>

<div class="card mt-4 mb-4">
  <div class="card-header">${heading}</div>
  <div class="card-body">
    <form action="${request.current_route_path()}" method="post">
      <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
      <div class="mb-3">
        ${form.name.label}
        ${form.name(class_="form-control")}
      </div>
      <div class="mb-3">
        ${form.street.label}
        ${form.street(class_="form-control")}
      </div>
      <div class="mb-3">
        ${form.postcode.label}
        ${form.postcode(class_="form-control")}
      </div>
      <div class="mb-3">
        ${form.city.label}
        ${form.city(class_="form-control")}
      </div>
      <div class="mb-3">
        ${form.country.label}
        ${form.country(class_="form-control", **{"hx-get": f"{request.route_url('subdivision')}", "hx-target": "#subdivision"})}
      </div>
      <div class="mb-3">
        ${form.subdivision.label}
        ${form.subdivision(class_="form-control")}
      </div>
      <div class="mb-3">
        ${form.website.label}
        ${form.website(class_="form-control")}
      </div>
      <div class="mb-3">
        ${form.color.label}
        ${form.color(class_="form-control")}
      </div>
      <div class="mb-3">
        ${form.NIP.label}
        ${form.NIP(class_="form-control")}
      </div>
      <div class="mb-3">
        ${form.REGON.label}
        ${form.REGON(class_="form-control")}
      </div>
      <div class="mb-3">
        ${form.KRS.label}
        ${form.KRS(class_="form-control")}
      </div>
      <div class="mb-3">
        ${form.court.label}
        ${form.court(class_="form-control")}
      </div>
      <div class="mb-3">
        <button type="submit" class="btn btn-primary">${_("Submit")}</button>
      </div>
    </form>
  </div>
</div>