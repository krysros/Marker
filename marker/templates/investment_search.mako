<%inherit file="layout.mako"/>

<div class="card">
  <div class="card-header">
    Znajdź inwestycję
  </div>
  <div class="card-body">
    <form action="${request.route_url('investment_results')}">
      <div class="form-group">
        <label for="name">Nazwa</label>
        <input type="text" class="form-control" id="name" name="name">
      </div>
      <div class="form-group">
        <label for="city">Miasto</label>
        <input type="text" class="form-control" id="city" name="city">
      </div>
      <div class="form-group">
        <label for="voivodeship">Województwo</label>
        <select class="form-control" id="voivodeship" name="voivodeship">
          % for k, v in voivodeships.items():
          <option value="${k}">${v}</option>
          % endfor
        </select>
      </div>
      <div class="form-group"> 
        <button type="submit" class="btn btn-primary">Szukaj</button>
      </div>
    </form>
  </div>
</div>