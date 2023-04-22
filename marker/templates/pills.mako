<%def name="pills(pills)">
  <ul class="nav nav-pills">
  % for pill in pills:
    <li class="nav-item">
    % if request.url == pill["url"]:
      <a class="nav-link active" aria-current="page" href="${pill['url']}">
    % else:
      <a class="nav-link" href="${pill['url']}">  
    % endif
      % if pill["icon"]:
        <i class="bi bi-${pill['icon']}"></i>
      % endif
      % if pill["title"]:
        ${pill["title"]}
      % endif
      % if pill["count"]:
        <span class="badge text-bg-secondary">
          <div hx-get="${pill['count']}" hx-trigger="${pill['event']} from:body">
            ${pill.get("init-val", 0)}
          </div>
        </span>
      % endif
      </a>
    </li>
  % endfor
  </ul>
</%def>