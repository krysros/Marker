<%def name="pills(pills)">
  <ul class="nav nav-pills">
  % for pill in pills:
    <li class="nav-item">
    % if request.url == pill["url"]:
      <a class="nav-link active position-relative" aria-current="page" href="${pill['url']}">
        ${pill["title"]}
        % if pill["counter"]:
          <span class="badge text-bg-secondary">
            ${pill['counter']}
          </span>
        % endif
      </a>
    % else:
      <a class="nav-link" href="${pill['url']}">
        ${pill["title"]}
        % if pill["counter"]:
          <span class="badge text-bg-secondary">
            ${pill['counter']}
          </span>
        % endif
      </a>
    % endif
    </li>
  % endfor
  </ul>
</%def>