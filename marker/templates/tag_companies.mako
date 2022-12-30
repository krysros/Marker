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
          Firmy <span class="badge text-bg-secondary"><div id="tag-companies-counter" hx-get="${request.route_url('count_tag_companies', tag_id=tag.id, slug=tag.slug)}" hx-trigger="tagCompanyEvent from:body">${tag.count_companies}</div></span>
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('tag_projects', tag_id=tag.id, slug=tag.slug)}">
          Projekty <span class="badge text-bg-secondary">${tag.count_projects}</span>
        </a>
      </li>
    </ul>
  </div>
  <div>${button.map('tag_companies_map', tag_id=tag.id, slug=tag.slug)}</div>
</div>

<p class="lead">${tag.name}</p>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown('tag_companies', dd_filter, tag_id=tag.id, slug=tag.slug)}</div>
  <div>${button.dropdown('tag_companies', dd_sort, tag_id=tag.id, slug=tag.slug)}</div>
  <div class="me-auto">${button.dropdown('tag_companies', dd_order, tag_id=tag.id, slug=tag.slug)}</div>
  <div>${button.export('tag_companies_export', tag_id=tag.id, slug=tag.slug, _query={'filter': dd_filter._filter, 'sort': dd_sort._sort, 'order': dd_order._order})}</div>
</div>

<%include file="company_table.mako"/>