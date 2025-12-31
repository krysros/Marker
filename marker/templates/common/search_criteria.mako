<%namespace name="button" file="button.mako"/>

<%!
  import pycountry
%>

% if form:
  % if any(x for x in form.data.values() if x):
  <div class="alert alert-info" role="alert">
    <strong>${_("Search criteria")}: </strong>
    % for k, v in form.data.items():
      % if v:
        ${form[k].label.text}:
        % if k == "color":
          <strong>${colors.get(v)}</strong>;
        % elif k == "status":
          <strong>${statuses.get(v)}</strong>;
        % elif k == "parent":
          <strong>${parents.get(v)}</strong>;
        % elif k == "role":
          <strong>${roles.get(v)}</strong>;
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
  </div>
  <div class="alert alert-info" role="alert">
    % if request.matched_route.name.startswith("company"):
    <a href="${request.route_url('company_add_from_search', _query=request.query_string)}" class="alert-link">${_("Go to form...")}</a>
    % elif request.matched_route.name.startswith("project"):
    <a href="${request.route_url('project_add_from_search', _query=request.query_string)}" class="alert-link">${_("Go to form...")}</a>
    % endif
  </div>
  % endif
% endif