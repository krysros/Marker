<%inherit file="layout.mako"/>

<div class="card">
  <div class="card-header">
    Znajdź osobę
  </div>
  <div class="card-body">
    <form action="${request.route_url('person_results')}">
      <div class="mb-3">
        <label for="name">Imię i nazwisko</label>
        <input type="text" class="form-control" id="name" name="name">
      </div>
      <div class="mb-3">
        <label for="position">Stanowisko</label>
        <input type="text" class="form-control" id="position" name="position">
      </div>
      <div class="mb-3">
        <label for="phone">Telefon</label>
        <input type="text" class="form-control" id="phone" name="phone">
      </div>
      <div class="mb-3">
        <label for="email">Email</label>
        <input type="text" class="form-control" id="email" name="email">
      </div>
      <div class="mb-3"> 
        <button type="submit" class="btn btn-primary">Szukaj</button>
      </div>
    </form>
  </div>
</div>