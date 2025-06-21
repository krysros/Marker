% if request.session.peek_flash():
  % for message in request.session.pop_flash():
    <div hx-ext="remove-me">
      <div class="alert alert-${message.split(':')[0]}" role="alert" remove-me="3s">
        ${message.split(':')[1] | n}
      </div>
    </div>
  % endfor
% endif