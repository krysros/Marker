% for k, v in paginator:
% if loop.last:
<tr hx-get="${next_page}"
    hx-trigger="revealed"
    hx-swap="afterend">
% else:
<tr>
% endif
% if rel == 'cv' or rel == 'tv':
  <td>${states[k]}</td>
% else:
  <td>${k}</td>
% endif
  <td class="col-2">${v}</td>
</tr>
% endfor