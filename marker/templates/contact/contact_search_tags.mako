<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="card mt-4 mb-4">
  <div class="card-header">${heading}</div>
  <div class="card-body">
    <form action="${request.route_url('contact_search_tags_results')}" method="get">
      <label class="form-label">${_("Tags")}</label>
      <div id="tag-inputs" class="vstack gap-2">
        % if tags:
          % for index, value in enumerate(tags, start=1):
            <%include file="contact_tag_input_row.mako" args="row_id='tag-' + str(index), value=value"/>
          % endfor
        % else:
          <%include file="contact_tag_input_row.mako" args="row_id='tag-1', value=''"/>
        % endif
      </div>
      <div class="hstack gap-2 mt-3">
        <button type="button"
                class="btn btn-secondary"
                hx-get="${request.route_url('contact_search_tags_input')}"
                hx-target="#tag-inputs"
                hx-swap="beforeend">
          <i class="bi bi-plus-lg"></i>
        </button>
        <button type="submit" class="btn btn-primary">${_("Search")}</button>
      </div>
    </form>
  </div>
</div>
