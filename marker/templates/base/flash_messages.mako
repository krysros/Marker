% if request.session.peek_flash():
  % for message in request.session.pop_flash():
    <div class="alert alert-${message.split(':')[0]} alert-dismissible fade show" role="alert">
      ${message.split(':')[1] | n}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
  % endfor
% endif