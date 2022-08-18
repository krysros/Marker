% if form.errors:
  % for field_name, field_errors in form.errors.items():
    % for error in field_errors:
      <div class="alert alert-danger alert-dismissible fade show" role="alert">
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        <strong>${form[field_name].label}:</strong> ${error}
      </div>
    % endfor
  % endfor
% endif