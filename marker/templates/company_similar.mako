<%inherit file="layout.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>

<div class="card">
  <div class="card-body">
    ${dropdown.filter_button('company_similar', states, company_id=company.id, slug=company.slug)}
  </div>
</div>

<p class="lead">Firmy o profilu działalności zbliżonym do <a href="${request.route_url('company_view', company_id=company.id, slug=company.slug)}">${company.name}</a></p>
<%include file="company_table.mako"/>