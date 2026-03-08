<%def name="checkbox(obj, url, selected_ids=None, is_checked=False)">
<input class="form-check-input marker-select-item"
       type="checkbox"
       value="${obj.id}"
       autocomplete="off"
       ${"checked" if is_checked or (selected_ids is not None and obj.id in selected_ids) else ""}
       hx-post="${url}"
       hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
       hx-trigger="click"
       hx-swap="none">
</%def>

<%def name="select_all()">
<input class="form-check-input marker-select-all"
       type="checkbox"
       autocomplete="off"
       ${"checked" if request.session.get("select_all_states", {}).get(request.path_qs, False) else ""}
       hx-post="${request.path_qs + ('&' if '?' in request.path_qs else '?') + '_select_all=1'}"
       hx-vals='js:{checked: event.target.checked}'
       hx-trigger="click"
       hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
       hx-swap="none"
       aria-label="Select all">
</%def>