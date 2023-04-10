<%namespace name="checkbox" file="checkbox.mako"/>

<div class="hstack">
  <div class="me-auto">
    <p class="lead">
      ${checkbox.checkbox(contact, selected=request.identity.selected_contacts, url=request.route_url('contact_check', contact_id=contact.id, slug=contact.slug))}
      &nbsp;${contact.name}
    </p>
  </div>
</div>