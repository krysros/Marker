<%namespace name="checkbox" file="checkbox.mako"/>

<div class="hstack">
  <div class="me-auto">
    <p class="lead">
      ${checkbox.checkbox(company, url=request.route_url('company_check', company_id=company.id, slug=company.slug), is_checked=is_company_selected)}
      &nbsp;${company.name}
      % if company.color:
        <span class="badge text-bg-${company.color}">${_(company.color)}</span>
      % endif
    </p>
  </div>
</div>