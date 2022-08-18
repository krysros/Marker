<%inherit file="layout.mako"/>

<div class="card">
  <div class="card-header">
    Znajdź projekt
  </div>
  <div class="card-body">
    <form action="${request.route_url('project_results')}">
      <div class="mb-3">
        <label for="name">Nazwa</label>
        <input type="text" class="form-control" id="name" name="name">
      </div>
      <div class="mb-3">
        <label for="city">Miasto</label>
        <input type="text" class="form-control" id="city" name="city">
      </div>
      <div class="mb-3">
        <label for="state">Województwo</label>
        <select class="form-control" id="state" name="state">
          % for k, v in states.items():
          <option value="${k}">${v}</option>
          % endfor
        </select>
      </div>
      <div class="mb-3">
        <button type="submit" class="btn btn-primary">Szukaj</button>
      </div>
    </form>
  </div>
</div>