<%inherit file="layout.mako"/>

<div class="card">
  <div class="card-body">
    <div class="float-right">
      <a href="${request.route_url('comment_add', company_id=company.id)}" class="btn btn-info" role="button"><i class="fa fa-comment" aria-hidden="true"></i><div class="d-none d-sm-block"> Dodaj</div></a>
    </div>
  </div>
</div>

<p class="lead">Komentarze nt. firmy <a href="${request.route_url('company_view', company_id=company.id, slug=company.slug)}">${company.name}</a></p>
<%include file="comment_more.mako"/>