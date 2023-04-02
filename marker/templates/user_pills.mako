<%! from marker.forms.ts import TranslationString as _ %>

<%def name="pills(user)">
  <%
  user_pills = [
    {"title": _("User"), "route_name": "user_view"},
    {"title": _("Companies"), "route_name": "user_companies"},
    {"title": _("Projects"), "route_name": "user_projects"},
    {"title": _("Tags"), "route_name": "user_tags"},
    {"title": _("Contacts"), "route_name": "user_contacts"},
    {"title": _("Comments"), "route_name": "user_comments"},
  ]
  %>
  <ul class="nav nav-pills">
  % for pill in user_pills:
    <li class="nav-item">
    % if request.matched_route.name == pill["route_name"] or request.matched_route.name == '_map_'.join(pill['route_name'].split('_')):
      <a class="nav-link active" aria-current="page" href="${request.route_url(pill['route_name'], username=user.name)}">
        ${pill["title"]}
        % if not pill["route_name"].endswith("_view"):
          <span class="badge text-bg-secondary">
            ${getattr(user, pill["route_name"].replace("user_", "count_"))}
          </span>
        % endif
      </a>
    % else:
      <a class="nav-link" href="${request.route_url(pill['route_name'], username=user.name)}">
        ${pill["title"]}
        % if not pill["route_name"].endswith("_view"):
          <span class="badge text-bg-secondary">
            ${getattr(user, pill["route_name"].replace("user_", "count_"))}
          </span>
        % endif
      </a>
    % endif
    </li>
  % endfor
  </ul>
</%def>