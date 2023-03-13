<div class="table-responsive">
  <table class="${'table table-dark' if request.session.get('color_scheme', 'light') == 'dark' else 'table'} table-striped">
    <thead>
      <tr>
        <th>#</th>
        <th>Imię i nazwisko</th>
        <th>Firma / Projekt</th>
        <th>Rola</th>
        <th>Telefon</th>
        <th>Email</th>
        <th>Utworzono</th>
        <th>Zmodyfikowano</th>
        <th class="col-2">Akcja</th>
      </tr>
    </thead>
    <tbody>
      <%include file="contact_more.mako"/>
    </tbody>
  </table>
</div>