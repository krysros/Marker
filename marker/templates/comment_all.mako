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
        ${form.typ.label}
        ${form.typ(class_="form-control")}
      </div>
      ${form.submit(class_="btn btn-primary")}
    </form>
  </div>
  <div>${button.dropdown(dd_order)}</div>
</div>

% if any(x for x in q.values() if x):
<div class="alert alert-info" role="alert">
  <strong>${_("Search criteria")}: </strong>
  % for k, v in q.items():
    ${k}:
    % if isinstance(v, list):
      <strong>${", ".join(v)}</strong>;
    % else:
      <strong>${v}</strong>;
    % endif
  % endfor
</div>
% endif

<%include file="comment_more.mako" />