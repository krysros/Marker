% if request.session.peek_flash():
  % for message in request.session.pop_flash():
    <div class="alert alert-${message.split(':')[0]}" role="alert">
      ${message.split(':')[1] | n}
    </div>
  % endfor
% endif