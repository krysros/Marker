<%namespace name="checkbox" file="checkbox.mako"/>

<div class="hstack">
  <div class="me-auto">
    <p class="lead">
      ${checkbox.check_contact(contact)}
      &nbsp;${contact.name}
    </p>
  </div>
</div>