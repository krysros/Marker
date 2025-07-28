<%def name="checkbox(obj, selected, url)">
<input class="form-check-input"
       type="checkbox"
       value="${obj.id}"
       autocomplete="off"
       ${"checked" if obj in selected else ""}
       hx-post="${url}"
       hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
       hx-trigger="click"
       hx-swap="none">
</%def>