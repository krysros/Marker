% if request.session.peek_flash():
  % for message in request.session.pop_flash():
    <% 
      alert_type, separator, alert_message = message.partition(':')
      if not separator:
          alert_type = "info"
          alert_message = message
    %>
    <div class="alert alert-${alert_type} alert-dismissible fade show" role="alert">
      ${alert_message | n}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
  % endfor
% endif