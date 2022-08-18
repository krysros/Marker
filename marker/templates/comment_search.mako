<%inherit file="layout.mako"/>

<div class="card">
  <div class="card-header">
    Znajdź komentarz
  </div>
  <div class="card-body">
    <form action="${request.route_url('comment_results')}">
      <div class="mb-3">
        <label for="comment">Komentarz</label>
        <input type="text" class="form-control" id="comment" name="comment">
      </div>
      <div class="mb-3"> 
        <button type="submit" class="btn btn-primary">Szukaj</button>
      </div>
    </form>
  </div>
</div>