<script>
  navigator.geolocation.getCurrentPosition((position) => {
    let latitude = position.coords.latitude;
    let longitude = position.coords.longitude;
  
    let map = L.map('map').setView([latitude, longitude], 5);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '© OpenStreetMap'
    }).addTo(map);
    let markers = L.markerClusterGroup({
      chunkedLoading: true,
      maxClusterRadius: 50,
    });
  
    async function populate() {
  
      const requestURL = "${url}";
      const request = new Request(requestURL);
  
      const response = await fetch(request);
      const items = await response.json();
  
      for (let i = 0; i < items.length; i++) {
        let a = items[i];
        let title = `<%text><b>${a.name}</b><br>Ulica: ${a.street}<br>Miasto: ${a.city}<br>Woj.: ${a.state}<br>Kraj: ${a.country}</%text>`;
        if (a.latitude != null && a.longitude != null) {
          let marker = L.marker(new L.LatLng(a.latitude, a.longitude), { title: title });
          marker.bindPopup(title);
          markers.addLayer(marker);
        }
      }
    }
    populate();
    map.addLayer(markers);
  })
</script>