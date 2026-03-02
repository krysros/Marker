<%page args="row_id='company-tag-1', value='', remove_route='company_add_tag_input_remove'"/>

<div class="tag-input-row">
  <div class="input-group">
    <input type="text"
           class="form-control"
           name="tag"
           value="${value}"
           placeholder="${_('Tag')}"
           aria-label="${_('Tag')}"
           list="tags-${row_id}"
           autocomplete="off"
           maxlength="200"
           hx-get="${request.route_url('tag_select')}"
           hx-target="#tag-select-list-${row_id}"
           hx-swap="innerHTML"
           hx-trigger="keyup changed delay:250ms"
           hx-vals='{"list_id": "tags-${row_id}"}'>
    <button type="button"
            class="btn btn-outline-danger"
            title="${_('Action')}"
            aria-label="${_('Action')}"
            hx-get="${request.route_url(remove_route)}"
            hx-target="closest .tag-input-row"
            hx-swap="outerHTML">
      <i class="bi bi-dash-lg"></i>
    </button>
  </div>
  <div id="tag-select-list-${row_id}" class="mt-1"></div>
</div>
