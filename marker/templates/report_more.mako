% for k, v in paginator:
% if loop.last:
<tr hx-get="${next_page}"
    hx-trigger="revealed"
    hx-swap="afterend">
% else:
<tr>
% endif
% if 'regions' in rel:
  <td>${regions[k]}</td>
% else:
  <td>${k}</td>
% endif
  <td class="col-2">${v}</td>
</tr>
% endfor