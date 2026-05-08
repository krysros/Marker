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

<%def name="preserve_params(exclude)">
<%
  skip = set(exclude)
%>
% for k, v in q.items():
  % if k not in skip:
    % if isinstance(v, list):
      % for item in v:
        <input type="hidden" name="${k}" value="${item}">
      % endfor
    % elif v is not None and str(v) != '':
      <input type="hidden" name="${k}" value="${v}">
    % endif
  % endif
% endfor
</%def>

<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  <div class="dropdown">
    <button type="button" class="btn btn-sm btn-secondary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside">
      % if q.get('object_category') or q.get('stage') or q.get('role'):
        <i class="bi bi-tag-fill"></i>
      % else:
        <i class="bi bi-tag"></i>
      % endif
      ${_("Category")}
    </button>
    <form class="dropdown-menu p-3" style="min-width: 280px;" method="get">
      ${preserve_params({'object_category', 'stage', 'role'})}
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
      <div class="hstack gap-2">
        <button type="submit" class="btn btn-primary btn-sm">${_("Submit")}</button>
        <% clear_q = {k: v for k, v in q.items() if k not in ('object_category', 'stage', 'role')} %>
        <a class="btn btn-outline-secondary btn-sm" href="${request.current_route_url(_query=clear_q)}">${_("Clear")}</a>
      </div>
    </form>
  </div>
  <div class="dropdown">
    <button type="button" class="btn btn-sm btn-secondary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside">
      % if q.get('currency') or q.get('value_net_from') or q.get('value_net_to') or q.get('value_gross_from') or q.get('value_gross_to') or q.get('unit_price_net_from') or q.get('unit_price_net_to') or q.get('unit_price_gross_from') or q.get('unit_price_gross_to'):
        <i class="bi bi-cash-fill"></i>
      % else:
        <i class="bi bi-cash"></i>
      % endif
      ${_("Value")}
    </button>
    <form class="dropdown-menu p-3" style="min-width: 320px;" method="get">
      ${preserve_params({'currency', 'value_net_from', 'value_net_to', 'value_gross_from', 'value_gross_to', 'unit_price_net_from', 'unit_price_net_to', 'unit_price_gross_from', 'unit_price_gross_to'})}
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
        <button type="submit" class="btn btn-primary btn-sm">${_("Submit")}</button>
        <% clear_q = {k: v for k, v in q.items() if k not in ('currency', 'value_net_from', 'value_net_to', 'value_gross_from', 'value_gross_to', 'unit_price_net_from', 'unit_price_net_to', 'unit_price_gross_from', 'unit_price_gross_to')} %>
        <a class="btn btn-outline-secondary btn-sm" href="${request.current_route_url(_query=clear_q)}">${_("Clear")}</a>
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
