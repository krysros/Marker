<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-2">
  <h2 class="mb-0 text-nowrap flex-grow-1 flex-shrink-1">
    <i class="bi bi-buildings"></i> ${_("Companies marked with a star")}
    <span class="badge bg-secondary">${counter}</span>
  </h2>
  <div class="d-flex flex-wrap gap-2 justify-content-md-end w-100 w-md-auto">
    ${button.a(icon='map', color='secondary', url=request.route_url('user_map_companies_stars', username=user.name))}
    ${button.button(icon='star', color='warning', url=request.route_url('user_clear_companies_stars', username=user.name))}
    <% _contact_cols = [_('Contact name'), _('Contact role'), _('Contact phone'), _('Contact email')]; _export_cols = _contact_cols + [_('Company name'), _('Company street'), _('Company post code'), _('Company city'), _('Company subdivision'), _('Company country'), _('Company website'), _('Company NIP'), _('Company REGON'), _('Company KRS'), _('Tags')] %>
    ${button.dropdown_download_cols(request.route_url('user_export_companies_stars', username=user.name, _query=q), _export_cols)}
  </div>
</div>
<hr>

<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <%include file="company_filter.mako"/>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div>${button.dropdown_order(order_criteria)}</div>
</div>

<%include file="search_criteria.mako"/>

<%include file="company_table.mako"/>
