<%namespace name="checkbox" file="checkbox.mako"/>

<div class="hstack">
  <div class="me-auto">
    <p class="lead">
      ${checkbox.check_company(company)}
      &nbsp;${company.name}
    </p>
  </div>
</div>