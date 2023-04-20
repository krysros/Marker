<%def name="pills(pills)">
  <ul class="nav nav-pills">
  % for pill in pills:
    <li class="nav-item">
    % if request.url == pill["url"]:
      <a class="nav-link active position-relative" aria-current="page" href="${pill['url']}">
        ${pill["title"]}
        % if project.color != "default":
          <span class="position-absolute top-0 start-100 translate-middle p-2 bg-${project.color} border border-light rounded-circle">
            <span class="visually-hidden">Color</span>
          </span>
        % endif
        % if pill["count"]:
          <span class="badge text-bg-secondary">
            <div hx-get="${pill['count']}"
                 hx-trigger="${pill['event']} from:body">
              ${pill['counter']}
            </div>
          </span>
        % endif
      </a>
    % else:
      <a class="nav-link" href="${pill['url']}">
        ${pill["title"]}
        % if pill["count"]:
          <span class="badge text-bg-secondary">
            <div hx-get="${pill['count']}"
                 hx-trigger="${pill['event']} from:body">
              ${pill['counter']}
            </div>
          </span>
        % endif
      </a>
    % endif
    </li>
  % endfor
  </ul>
</%def>