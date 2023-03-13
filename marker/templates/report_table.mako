<div class="table-responsive">
  <table class="${'table table-dark' if request.session.get('color_scheme', 'light') == 'dark' else 'table'} table-striped">
    <thead>
      <tr>
        <th>Opis</th>
        <th class="col-2">Liczba</th>
      </tr>
    </thead>
    <tbody>
      <%include file="report_more.mako"/>
    </tbody>
  </table>
</div>