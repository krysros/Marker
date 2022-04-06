<%inherit file="layout.mako"/>

<div class="card">
  <div class="card-header">
    Znajdź osobę
  </div>
  <div class="card-body">
    <form action="${request.route_url('person_results')}">
      <div class="form-group">
        <label for="fullname">Imię i nazwisko</label>
        <input type="text" class="form-control" id="fullname" name="fullname">
      </div>
      <div class="form-group">
        <label for="position">Stanowisko</label>
        <input type="text" class="form-control" id="position" name="position">
      </div>
      <div class="form-group">
        <label for="phone">Telefon</label>
        <input type="text" class="form-control" id="phone" name="phone">
      </div>
      <div class="form-group">
        <label for="email">Email</label>
        <input type="text" class="form-control" id="email" name="email">
      </div>
      <div class="form-group"> 
        <button type="submit" class="btn btn-primary">Szukaj</button>
      </div>
    </form>
  </div>
</div>