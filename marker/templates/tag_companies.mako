<%inherit file="layout.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="card">
  <div class="card-header">
    <div class="row">
      <div class="col-4">
        <ul class="nav nav-tabs card-header-tabs">
          <li class="nav-item">
            <a class="nav-link" href="${request.route_url('tag_view', tag_id=tag.id, slug=tag.slug)}">Tag</a>
          </li>
          <li class="nav-item">
            <a class="nav-link active" aria-current="page" href="${request.route_url('tag_companies', tag_id=tag.id, slug=tag.slug)}">Firmy</a>
          </li>
        </ul>
      </div>
      <div class="col-8">
        <div class="float-end">
          ${dropdown.filter_button('tag_companies', states, tag_id=tag.id, slug=tag.slug)}
          ${dropdown.sort_button('tag_companies', dropdown_sort, tag_id=tag.id, slug=tag.slug)}
          ${dropdown.order_button('tag_companies', dropdown_order, tag_id=tag.id, slug=tag.slug)}
          ${button.export('tag_companies_export', tag_id=tag.id, _query={'filter': filter, 'sort': sort, 'order': order})}
        </div>
      </div>
    </div>
  </div>
  <div class="card-body">
    Firmy oznaczone tagiem <strong>${tag.name}</strong>
  </div>
</div>

<%include file="company_table.mako"/>