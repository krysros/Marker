<%inherit file="layout.mako"/>

<div class="card">
  <div class="card-body">
    <div class="float-end">
      <a href="${request.route_url('comment_add', company_id=company.id)}" class="btn btn-success" role="button">Dodaj</a>
    </div>
  </div>
</div>

<p class="lead">Komentarze nt. firmy <a href="${request.route_url('company_view', company_id=company.id, slug=company.slug)}">${company.name}</a></p>
<%include file="comment_more.mako"/>