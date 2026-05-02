<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-currency-exchange"></i> ${_("Project Prices")}
  <span class="badge bg-secondary">${counter}</span>
</h2>

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

<div class="table-responsive">
  <table class="table table-striped table-hover">
    <thead>
      <tr>
        <th>${_("Project")}</th>
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
      <%include file="prices_more.mako"/>
    </tbody>
  </table>
</div>
