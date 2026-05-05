<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-2">
  <h2 class="mb-0 text-nowrap flex-grow-1 flex-shrink-1">
    <i class="bi bi-currency-exchange"></i> ${_("Project Prices")}
    <span class="badge bg-secondary">${counter}</span>
  </h2>
  <div class="d-flex flex-wrap gap-2 justify-content-md-end w-100 w-md-auto">
    <% from marker.utils.export_columns import prices_cols; _export_cols = prices_cols(_) %>
    ${button.dropdown_download_cols(request.route_url('prices_export', _query=q), _export_cols)}
  </div>
</div>

<hr>

<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <div class="dropdown">
    <button type="button" class="btn btn-secondary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside">
      <i class="bi bi-filter"></i> ${_("Filter")}
    </button>
    <form class="dropdown-menu p-4" style="min-width: 340px;" method="get">
      <input type="hidden" name="sort" value="${q.get('sort', 'project_name')}">
      <input type="hidden" name="order" value="${q.get('order', 'asc')}">
      <div class="mb-3">
        <label for="prices-filter-object-category" class="form-label">${_("Object category")}</label>
        <select id="prices-filter-object-category" class="form-select" name="object_category">
          <option value="">${_("All")}</option>
          % for v, l in object_categories.items():
          <option value="${v}" ${"selected" if q.get("object_category") == v else ""}>${l}</option>
          % endfor
        </select>
      </div>
      <div class="mb-3">
        <label for="prices-filter-stage" class="form-label">${_("Stage")}</label>
        <select id="prices-filter-stage" class="form-select" name="stage">
          <option value="">${_("All")}</option>
          % for v, l in stage_choices:
          <option value="${v}" ${'selected' if q.get('stage') == v else ''}>${l}</option>
          % endfor
        </select>
      </div>
      <div class="mb-3">
        <label for="prices-filter-role" class="form-label">${_("Role")}</label>
        <select id="prices-filter-role" class="form-select" name="role">
          <option value="">${_("All")}</option>
          % for v, l in role_choices:
          <option value="${v}" ${'selected' if q.get('role') == v else ''}>${l}</option>
          % endfor
        </select>
      </div>
      <div class="mb-3">

        <label for="prices-filter-currency" class="form-label">${_("Currency")}</label>
        <select id="prices-filter-currency" class="form-select" name="currency">
          % for v, l in currency_choices:
          <option value="${v}" ${'selected' if q.get('currency') == v else ''}>${l}</option>
          % endfor
        </select>
      </div>
      <div class="mb-3">
        <label class="form-label">${_("Net value")}</label>
        <div class="input-group">
          <input type="number" class="form-control" name="value_net_from" placeholder="${_('From')}" value="${q.get('value_net_from', '')}" min="0" step="0.01">
          <input type="number" class="form-control" name="value_net_to" placeholder="${_('To')}" value="${q.get('value_net_to', '')}" min="0" step="0.01">
        </div>
      </div>
      <div class="mb-3">
        <label class="form-label">${_("Gross value")}</label>
        <div class="input-group">
          <input type="number" class="form-control" name="value_gross_from" placeholder="${_('From')}" value="${q.get('value_gross_from', '')}" min="0" step="0.01">
          <input type="number" class="form-control" name="value_gross_to" placeholder="${_('To')}" value="${q.get('value_gross_to', '')}" min="0" step="0.01">
        </div>
      </div>
      <div class="mb-3">
        <label class="form-label">${_("Net / m\u00b2")}</label>
        <div class="input-group">
          <input type="number" class="form-control" name="unit_price_net_from" placeholder="${_('From')}" value="${q.get('unit_price_net_from', '')}" min="0" step="0.01">
          <input type="number" class="form-control" name="unit_price_net_to" placeholder="${_('To')}" value="${q.get('unit_price_net_to', '')}" min="0" step="0.01">
        </div>
      </div>
      <div class="mb-3">
        <label class="form-label">${_("Gross / m\u00b2")}</label>
        <div class="input-group">
          <input type="number" class="form-control" name="unit_price_gross_from" placeholder="${_('From')}" value="${q.get('unit_price_gross_from', '')}" min="0" step="0.01">
          <input type="number" class="form-control" name="unit_price_gross_to" placeholder="${_('To')}" value="${q.get('unit_price_gross_to', '')}" min="0" step="0.01">
        </div>
      </div>
      <div class="hstack gap-2">
        <button type="submit" class="btn btn-primary">${_("Submit")}</button>
        <a class="btn btn-outline-secondary" href="${request.route_url('prices_all')}">${_("Clear")}</a>
      </div>
    </form>
  </div>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div>${button.dropdown_order(order_criteria)}</div>
</div>

<%def name="rows()">
% for row in paginator:
% if loop.last:
<tr hx-get="${next_page}" hx-trigger="revealed" hx-swap="afterend">
% else:
<tr>
% endif
  <td>
    <a href="${request.route_url('project_view', project_id=row.project.id, slug=row.project.slug)}">${row.project.name}</a>
    % if row.project.usable_area:
    <br><small class="text-body-secondary">${_("Usable area")}: ${"{:,.2f}".format(row.project.usable_area)} m2</small>
    % endif
  </td>
  <td><small>${object_categories.get(row.project.object_category, row.project.object_category or "---")}</small></td>
  <td>
    <a href="${request.route_url('company_view', company_id=row.company.id, slug=row.company.slug)}">${row.company.name}</a>
  </td>
  <td>${stages.get(row.activity.stage, row.activity.stage or "---")}</td>
  <td>${roles.get(row.activity.role, row.activity.role or "---")}</td>
  <td>${row.activity.currency or "---"}</td>
  <td class="text-end">
    % if row.activity.value_net is not None:
    ${"{:,.2f}".format(row.activity.value_net)}
    % else:
    ---
    % endif
  </td>
  <td class="text-end">
    % if row.activity.value_gross is not None:
    ${"{:,.2f}".format(row.activity.value_gross)}
    % else:
    ---
    % endif
  </td>
  <td class="text-end">
    % if row.unit_price_net is not None:
    ${"{:,.2f}".format(row.unit_price_net)}
    % else:
    ---
    % endif
  </td>
  <td class="text-end">
    % if row.unit_price_gross is not None:
    ${"{:,.2f}".format(row.unit_price_gross)}
    % else:
    ---
    % endif
  </td>
</tr>
% endfor
</%def>

<div class="table-responsive">
  <table class="table table-striped table-hover">
    <thead>
      <tr>
        <th>${_("Project")}</th>
        <th>${_("Object category")}</th>
        <th>${_("Company")}</th>
        <th>${_("Stage")}</th>
        <th>${_("Role")}</th>
        <th>${_("Currency")}</th>
        <th class="text-end">${_("Net value")}</th>
        <th class="text-end">${_("Gross value")}</th>
        <th class="text-end">${_("Net / m²")}</th>
        <th class="text-end">${_("Gross / m²")}</th>
      </tr>
    </thead>
    <tbody>
      ${rows()}
    </tbody>
  </table>
</div>
