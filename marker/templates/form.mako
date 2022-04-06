<%inherit file="layout.mako"/>  

<div class="card">
  <div class="card-header">${heading}</div>
  <div class="card-body">
    ${rendered_form | n}
  </div>
</div>