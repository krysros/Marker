<%inherit file="layout.mako" />
<%namespace name="button" file="button.mako" />

<h2>
  <i class="bi bi-chat-left-text"></i> ${_("Comments")}
  <span class="badge bg-secondary"><div hx-get="${request.route_url('comment_count')}" hx-trigger="commentEvent from:body">${counter}</div></span>
  <div class="float-end">
    ${button.a_button(icon='search', color='primary', url=request.route_url('comment_search'))}
  </div>
</h2>

<hr>

<div class="hstack gap-2 mb-4">
  <div class="dropdown">
    <button type="button" class="btn btn-secondary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside">
      <i class="bi bi-filter"></i> ${_("Filter")}
    </button>
    <form class="dropdown-menu p-4">
      ${form.comment(class_="form-control")}
      <div class="mb-3">
        ${form.parent.label}
        ${form.parent(class_="form-control")}
      </div>
      <input class="btn btn-primary" id="submit" name="submit" type="submit" value="${_('Submit')}">
    </form>
  </div>
  <div>${button.dropdown(dd_order)}</div>
</div>

<%include file="search_criteria.mako"/>

<%include file="comment_more.mako" />