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
        % else:
          <strong>${v}</strong>;
        % endif
      % endif
    % endfor
  </div>
  % endif
% endif