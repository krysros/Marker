<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="checkbox" file="checkbox.mako"/>
<%namespace name="pills" file="pills.mako"/>
<%namespace name="modals" file="modals.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.company_pill(company)}</div>
  <div>
    % if request.identity.role == 'editor' or 'admin':
    <button id="btn-add-contact" type="button" class="btn btn-success" data-bs-toggle="modal" data-bs-target="#modal-add-contact">
      <i class="bi bi-plus-lg"></i>
    </button>
    % else:
    <button type="button" class="btn btn-success" disabled><i class="bi bi-plus-lg"></i></button>
    % endif
  </div>
</div>

<%include file="company_lead.mako"/>

<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th class="col-1">#</th>
        <th>Imię i nazwisko</th>
        <th>Rola</th>
        <th>Telefon</th>
        <th>Email</th>
        <th class="col-2">Akcja</th>
      </tr>
    </thead>
    <tbody id="new-contact">
      % for contact in company.contacts:
        <%include file="contact_row.mako" args="contact=contact"/>
      % endfor
    </tbody>
  </table>
</div>

${modals.add_contact(company)}