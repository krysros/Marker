<%inherit file="layout.mako"/>

<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th>Imię i nazwisko</th>
        <th>Firma</th>
        <th>Telefon</th>
        <th>Email</th>
      </tr>
    </thead>
    <tbody>
      <%include file="person_more.mako"/>
    </tbody>
  </table>
</div>