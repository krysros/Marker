<%inherit file="layout.mako"/>

<div class="card">
  <div class="card-header">
    Znajdź tag
  </div>
  <div class="card-body">
    <form action="${request.route_url('tag_results')}">
      <div class="mb-3">
        <label for="name">Nazwa</label>
        <input type="text" class="form-control" id="name" name="name">
      </div>
      <div class="mb-3">
        <button type="submit" class="btn btn-primary">Szukaj</button>
      </div>
    </form>
  </div>
</div>