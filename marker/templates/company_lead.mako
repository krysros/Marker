<%namespace name="checkbox" file="checkbox.mako"/>

<div class="hstack">
  <div class="me-auto">
    <p class="lead">
      ${checkbox.checkbox(company, selected=request.identity.selected_companies, url=request.route_url('company_check', company_id=company.id, slug=company.slug))}
      &nbsp;${company.name}
      % if company.color:
        <span class="badge text-bg-${company.color}">${_(company.color)}</span>
      % endif
    </p>
  </div>
</div>