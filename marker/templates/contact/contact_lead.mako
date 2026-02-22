<%namespace name="checkbox" file="checkbox.mako"/>

<div class="hstack">
  <div class="me-auto">
    <p class="lead">
      ${checkbox.checkbox(contact, selected=request.identity.selected_contacts, url=request.route_url('contact_check', contact_id=contact.id, slug=contact.slug))}
      &nbsp;${contact.name}
      % if contact.color:
        <span class="badge text-bg-${contact.color}">${_(contact.color)}</span>
      % endif
    </p>
  </div>
</div>