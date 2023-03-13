<div class="table-responsive">
  <table class="${'table table-dark' if request.session.get('color_scheme', 'light') == 'dark' else 'table'} table-striped">
    <thead>
      <tr>
        <th>Nazwa</th>
        <th>Imię i nazwisko</th>
        <th>Email</th>
        <th>Rola</th>
        <th>Dodano</th>
        <th>Zmodyfikowano</th>
      </tr>
    </thead>
    <tbody>
      <%include file="user_more.mako"/>
    </tbody>
  </table>
</div>