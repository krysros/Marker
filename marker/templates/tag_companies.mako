<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">
    <ul class="nav nav-pills">
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('tag_view', tag_id=tag.id, slug=tag.slug)}">Tag</a>
      </li>
      <li class="nav-item">
        <a class="nav-link active" aria-current="page" href="${request.route_url('tag_companies', tag_id=tag.id, slug=tag.slug)}">
          Firmy <span class="badge text-bg-secondary"><div id="tag-companies-counter" hx-get="${request.route_url('count_tag_companies', tag_id=tag.id, slug=tag.slug)}" hx-trigger="tagCompanyEvent from:body">${c_companies}</div></span>
        </a>
      </li>
    </ul>
  </div>
  <div>${button.map('tag_map', tag_id=tag.id, slug=tag.slug)}</div>
</div>

<p class="lead">${tag.name}</p>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown('tag_companies', items=colors, criterion=filter, typ='filter', title='Kolor', tag_id=tag.id, slug=tag.slug)}</div>
  <div>${button.dropdown('tag_companies', items=dropdown_sort, criterion=sort, typ='sort', title='Sortuj', tag_id=tag.id, slug=tag.slug)}</div>
  <div class="me-auto">${button.dropdown('tag_companies', items=dropdown_order, criterion=order, typ='order', title='Kolejność', tag_id=tag.id, slug=tag.slug)}</div>
  <div>${button.export('tag_companies_export', tag_id=tag.id, slug=tag.slug, _query={'filter': filter, 'sort': sort, 'order': order})}</div>
</div>

<%include file="company_table.mako"/>