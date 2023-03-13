<div class="table-responsive">
  <table class="${'table table-dark' if request.session.get('color_scheme', 'light') == 'dark' else 'table'} table-striped">
    <thead>
      <tr>
        <th class="col-1">#</th>
        <th>Firma</th>
        <th>Miasto</th>
        <th>Region</th>
        <th>Utworzono</th>
        <th>Zmodyfikowano</th>
        <th>Rekomendacje</th>
        <th>Komentarze</th>
        <th class="col-2">Akcja</th>
      </tr>
    </thead>
    <tbody>
      <%include file="company_more.mako"/>
    </tbody>
  </table>
</div>