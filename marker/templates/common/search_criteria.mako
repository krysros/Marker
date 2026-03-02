<%namespace name="button" file="button.mako"/>

<%!
  import pycountry
%>

% if form:
  <% tags = q.get("tag", []) if q else [] %>
  % if any(x for x in form.data.values() if x) or tags:
  <div class="alert alert-info" role="alert">
    <strong>${_("Search criteria")}: </strong>
    % for k, v in form.data.items():
      % if v:
        ${form[k].label.text}:
        % if k == "color":
          <strong>${colors.get(v)}</strong>;
        % elif k == "status":
          <strong>${statuses.get(v)}</strong>;
        % elif k == "category":
          <strong>${categories.get(v)}</strong>;
        % elif k == "role":
          <strong>${form.data["role"]}</strong>;
        % elif k == "country":
          <strong>${pycountry.countries.get(alpha_2=v).name}</strong>;
        % elif k == "subdivision":
          % for i in v:
            <strong>${getattr(pycountry.subdivisions.get(code=i), "name", "---")}</strong>;
          % endfor
        % elif k == "stage":
          <strong>${stages.get(v)}</strong>;
        % elif k == "delivery_method":
          <strong>${project_delivery_methods.get(v)}</strong>;
        % else:
          <strong>${v}</strong>;
        % endif
      % endif
    % endfor
    % if tags:
      ${_("Tags")}: <strong>${"; ".join(tags)}</strong>;
    % endif
  </div>
  <% add_query = {**form.data} %>
  % if tags:
    <% add_query["tag"] = tags %>
  % endif
  % if request.matched_route.name.startswith("company"):
  <div class="alert alert-info" role="alert">
    ${_("Don't see what you're looking for?")}
    <a href="${request.route_url('company_add', _query=add_query)}" class="alert-link">${_("Go to the form and add...")}</a>
  </div>
  % elif request.matched_route.name.startswith("project"):
  <div class="alert alert-info" role="alert">
    ${_("Don't see what you're looking for?")}
    <a href="${request.route_url('project_add', _query=add_query)}" class="alert-link">${_("Go to the form and add...")}</a>
  </div>
  % endif
  % endif
% endif