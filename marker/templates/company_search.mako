<%inherit file="layout.mako"/>

<div class="card">
  <div class="card-header">
    Znajdź firmę
  </div>
  <div class="card-body">
    <form action="${request.route_url('company_results')}">
      <div class="form-group">
        <label for="name">Nazwa</label>
        <input type="text" class="form-control" id="name" name="name">
      </div>
      <div class="form-group">
        <label for="street">Ulica</label> 
        <input type="text" class="form-control" id="street" name="street">
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
        <label for="phone">Telefon</label> 
        <input type="text" class="form-control" id="phone" name="phone">
      </div>
      <div class="form-group">
        <label for="email">Email</label>
        <input type="text" class="form-control" id="email" name="email">
      </div>
      <div class="form-group">
        <label for="www">WWW</label>
        <input type="text" class="form-control" id="www" name="www">
      </div>
      <div class="form-group">
        <label for="nip">NIP</label>
        <input type="text" class="form-control" id="nip" name="nip">
      </div>
      <div class="form-group">
        <label for="regon">REGON</label>
        <input type="text" class="form-control" id="regon" name="regon">
      </div>
      <div class="form-group">
        <label for="krs">KRS</label>
        <input type="text" class="form-control" id="krs" name="krs">
      </div>
      <div class="form-group"> 
        <button type="submit" class="btn btn-primary">Szukaj</button>
      </div>
    </form>
  </div>
</div>