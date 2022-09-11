<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th>Tag</th>
        <th class="col-2">Akcja</th>
      </tr>
    </thead>
    <tbody>
      % for tag in company.tags:
      <tr>
        <td><a href="#" hx-get="${request.route_url('tag_view', tag_id=tag.id, slug=tag.slug)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">${tag.name}</a></td>
        <td class="col-2"><button class="btn btn-secondary btn-sm" hx-post="${request.route_url('delete_tag', company_id=company.id, tag_id=tag.id)}" hx-confirm="Czy jesteś pewny?" hx-target="closest tr" hx-swap="outerHTML swap:1s">Usuń</button></td>
      </tr>
      % endfor
    </tbody>
  </table>
</div>