<%! from marker.forms.ts import TranslationString as _ %>

<%def name="pills(tag)">
  <%
  tag_pills = [
    {"title": _("Tag"), "route_name": "tag_view", "event": "tagEvent"},
    {"title": _("Companies"), "route_name": "tag_companies", "event": "tagEvent"},
    {"title": _("Projects"), "route_name": "tag_projects", "event": "tagEvent"},
  ]
  %>
  <ul class="nav nav-pills">
  % for pill in tag_pills:
    <li class="nav-item">
    % if request.matched_route.name == pill["route_name"] or request.matched_route.name == '_map_'.join(pill['route_name'].split('_')):
      <a class="nav-link active position-relative" aria-current="page" href="${request.route_url(pill['route_name'], tag_id=tag.id, slug=tag.slug)}">
        ${pill["title"]}
        % if not pill["route_name"].endswith("_view"):
          <span class="badge text-bg-secondary">
            <div hx-get="${request.route_url('_count_'.join(pill['route_name'].split('_')), tag_id=tag.id, slug=tag.slug)}"
                 hx-trigger="${pill['event']} from:body">
              ${getattr(tag, pill["route_name"].replace("tag_", "count_"))}
            </div>
          </span>
        % endif
      </a>
    % else:
      <a class="nav-link" href="${request.route_url(pill['route_name'], tag_id=tag.id, slug=tag.slug)}">
        ${pill["title"]}
        % if not pill["route_name"].endswith("_view"):
          <span class="badge text-bg-secondary">
            <div hx-get="${request.route_url('_count_'.join(pill['route_name'].split('_')), tag_id=tag.id, slug=tag.slug)}"
                 hx-trigger="${pill['event']} from:body">
              ${getattr(tag, pill["route_name"].replace("tag_", "count_"))}
            </div>
          </span>
        % endif
      </a>
    % endif
    </li>
  % endfor
  </ul>
</%def>