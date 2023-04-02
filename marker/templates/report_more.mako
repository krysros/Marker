<%!
  import pycountry
%>

% for k, v in paginator:
% if loop.last:
<tr hx-get="${next_page}"
    hx-trigger="revealed"
    hx-swap="afterend">
% else:
<tr>
% endif
% if "subdivisions" in rel:
  <td>${getattr(pycountry.subdivisions.get(code=k), "name", "---")}</td>
% else:
  <td>${k}</td>
% endif
  <td class="col-2">${v}</td>
</tr>
% endfor