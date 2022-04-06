<%inherit file="layout.mako"/>

<div class="card">
  <div class="card-header">
    Znajdź branżę
  </div>
  <div class="card-body">
    <form action="${request.route_url('branch_results')}">
      <div class="form-group">
        <label for="name">Nazwa</label>
        <input type="text" class="form-control" id="name" name="name">
      </div>
      <div class="form-group">
        <button type="submit" class="btn btn-primary">Szukaj</button>
      </div>
    </form>
  </div>
</div>