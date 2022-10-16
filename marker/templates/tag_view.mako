<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="card border-0">
  <div class="row">
    <div class="col-9">
      <ul class="nav nav-pills">
        <li class="nav-item">
          <a class="nav-link active" aria-current="page" href="${request.route_url('tag_view', tag_id=tag.id, slug=tag.slug)}">Tag</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="${request.route_url('tag_companies', tag_id=tag.id, slug=tag.slug)}">
            Firmy <span class="badge text-bg-secondary">${c_companies}</span>
          </a>
        </li>
      </ul>
    </div>
    <div class="col-3">
      <div class="float-end">
        ${button.edit('tag_edit', tag_id=tag.id, slug=tag.slug)}
        ${button.delete('tag_delete', tag_id=tag.id, slug=tag.slug)}    
      </div>
    </div>
  </div>
</div>

<div class="card">
  <div class="card-header"><i class="bi bi-tag"></i> ${tag.name}</div>
  <div class="card-body">
    <div id="map"></div>
  </div>
</div>

<div class="card">
  <div class="card-header"><i class="bi bi-clock"></i> Data modyfikacji</div>
  <div class="card-body">
    <p>
      Utworzono: ${tag.created_at.strftime('%Y-%m-%d %H:%M:%S')}
      % if tag.created_by:
        przez <a href="${request.route_url('user_view', username=tag.created_by.name)}">${tag.created_by.name}</a>
      % endif
      <br>
      % if tag.updated_at:
        Zmodyfikowano: ${tag.updated_at.strftime('%Y-%m-%d %H:%M:%S')}
        % if tag.updated_by:
          przez <a href="${request.route_url('user_view', username=tag.updated_by.name)}">${tag.updated_by.name}</a>
        % endif
      % endif
    </p>
  </div>
</div>

<script>
  navigator.geolocation.getCurrentPosition((position) => {
    let latitude = position.coords.latitude;
    let longitude = position.coords.longitude;
  
    var map = L.map('map').setView([latitude, longitude], 5);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap'
    }).addTo(map);
    var markers = L.markerClusterGroup({
      chunkedLoading: true,
      maxClusterRadius: 50,
    });
  
    async function populate() {
  
      const requestURL = "${request.route_url('tag_json', tag_id=tag.id, slug=tag.slug)}";
      const request = new Request(requestURL);
  
      const response = await fetch(request);
      const items = await response.json();
  
      for (var i = 0; i < items.length; i++) {
        var a = items[i];
        var title = a.name;
        if (a.latitude != null && a.longitude != null) {
          var marker = L.marker(new L.LatLng(a.latitude, a.longitude), { title: title });
          marker.bindPopup(title);
          markers.addLayer(marker);
        }
      }
    }
    populate();
    map.addLayer(markers);
  })
</script>