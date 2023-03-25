<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">
    <ul class="nav nav-pills">
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('tag_view', tag_id=tag.id, slug=tag.slug)}">Tag</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" aria-current="page" href="${request.route_url('tag_companies', tag_id=tag.id, slug=tag.slug)}">
          Firmy <span class="badge text-bg-secondary">${tag.count_companies}</span>
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link active" href="${request.route_url('tag_projects', tag_id=tag.id, slug=tag.slug)}">
          Projekty <span class="badge text-bg-secondary"><div hx-get="${request.route_url('tag_count_projects', tag_id=tag.id, slug=tag.slug)}" hx-trigger="projectEvent from:body">${tag.count_projects}</div></span>
        </a>
      </li>
    </ul>
  </div>
  <div>${button.map('tag_map_projects', tag_id=tag.id, slug=tag.slug)}</div>
</div>

<%include file="tag_lead.mako"/>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown('tag_projects', dd_filter, tag_id=tag.id, slug=tag.slug)}</div>
  <div>${button.dropdown('tag_projects', dd_sort, tag_id=tag.id, slug=tag.slug)}</div>
  <div class="me-auto">${button.dropdown('tag_projects', dd_order, tag_id=tag.id, slug=tag.slug)}</div>
  <div>${button.export('tag_export_projects', tag_id=tag.id, slug=tag.slug, _query={'filter': dd_filter._filter, 'sort': dd_sort._sort, 'order': dd_order._order})}</div>
</div>

<%include file="project_table.mako"/>