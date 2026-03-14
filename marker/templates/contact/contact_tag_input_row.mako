<%page args="row_id='tag-1', value=''"/>

<div class="tag-input-row input-group">
  <input type="text"
         class="form-control"
         name="tag"
         value="${value}"
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
        hx-get="${request.route_url('search_tags_input_remove')}"
          hx-target="closest .tag-input-row"
          hx-swap="outerHTML">
    <i class="bi bi-dash-lg"></i>
  </button>
</div>
<div id="tag-select-list-${row_id}"></div>
