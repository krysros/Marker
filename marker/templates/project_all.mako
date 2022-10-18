<%inherit file="layout.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="card border-0">
  <div class="row">
    <div class="col-3">
      <ul class="nav nav-pills">
        <li class="nav-item">
          <a class="nav-link active" aria-current="page" href="${request.route_url('project_all')}">Tabela</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="${request.route_url('project_map')}">Mapa</a>
        </li>
      </ul>
    </div>
    <div class="col-9">
      <div class="float-end">
        ${dropdown.filter_button('project_all', dropdown_status)}
        ${dropdown.sort_button('project_all', dropdown_sort)}
        ${dropdown.order_button('project_all', dropdown_order)}
        ${button.search('project_search')}
        ${button.add('project_add')}
      </div>
    </div>
  </div>
</div>

<%include file="project_table.mako"/>