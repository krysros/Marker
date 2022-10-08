<%inherit file="layout.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="card border-0">
  <div class="row">
    <div class="col-3">
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
    <div class="col-9">
      <div class="float-end">
        ${dropdown.filter_button('tag_companies', states, tag_id=tag.id, slug=tag.slug)}
        ${dropdown.sort_button('tag_companies', dropdown_sort, tag_id=tag.id, slug=tag.slug)}
        ${dropdown.order_button('tag_companies', dropdown_order, tag_id=tag.id, slug=tag.slug)}
        ${button.export('tag_companies_export', tag_id=tag.id, _query={'filter': filter, 'sort': sort, 'order': order})}
        % if request.identity.role == 'editor':
          <button id="btn-add-company-to-tag" type="button" class="btn btn-success" data-bs-toggle="modal" data-bs-target="#add-company-to-tag-modal">
            Dodaj
          </button>
        % else:
          <button type="button" class="btn btn-success btn-sm" disabled>Dodaj</button>
        % endif
      </div>
    </div>
  </div>
</div>

<div id="tag-companies">
  <%include file="company_list_tag.mako"/>
</div>

<div class="modal fade" id="add-company-to-tag-modal" tabindex="-1" aria-labelledby="add-company-to-tag-modal-label" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <form hx-post="${request.route_url('add_company_to_tag', tag_id=tag.id, slug=tag.slug)}" hx-target="#tag-companies" hx-swap="innerHTML show:window:top">
        <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
        <div class="modal-header">
          <h5 class="modal-title" id="add-company-to-tag-modal-label">Dodaj firmę</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label for="company-name" class="form-label">Nazwa</label>
            <input list="companies" type="text" class="form-control" id="company-name" name="name" autocomplete="off" hx-get="${request.route_url('company_select')}" hx-target="#company-list"  hx-swap="innerHTML" hx-trigger="keyup changed delay:250ms" required maxlength="100">
            <div id="company-list"></div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Zamknij</button>
          <button type="submit" class="btn btn-primary" id="btn-save-company">Zapisz</button>
        </div>
      </form>
    </div>
  </div>
</div>

<script>
  // Hide Company Modal
  var modalCompanyEl = document.getElementById("add-company-to-tag-modal");
  var modalCompany = new bootstrap.Modal(modalCompanyEl);
  document.getElementById("btn-save-company").addEventListener("click", function () {
    modalCompany.hide();
  });
  // Clear input fields in Company Modal
  var btnAddCompany = document.getElementById("btn-add-company-to-tag");
  btnAddCompany.addEventListener('click', function handleClick(event) {
    var companyName = document.getElementById("company-name");
    companyName.value = '';
  });
</script>