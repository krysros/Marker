<script src="${request.static_url('marker:static/js/marker-lazy-load.js')}"></script>
<script>
  navigator.geolocation.getCurrentPosition((position) => {
    let latitude = position.coords.latitude;
    let longitude = position.coords.longitude;
  
    let map = L.map('map').setView([latitude, longitude], 5);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '© OpenStreetMap'
    }).addTo(map);
  
    // Initialize lazy marker loader with the data URL
    const lazyLoader = new LazyMarkerLoader(map, "${url}", {
      clusterOptions: {
        chunkedLoading: true,
        maxClusterRadius: 50,
      },
      debounceDelay: 500,
      autoLoad: true
    });
    
    lazyLoader.init();
  })
</script>