<script src="${request.static_url('marker:static/js/marker-lazy-load.js')}"></script>
<script>
  const fallbackCenter = [52.2297, 21.0122];
  const fallbackZoom = 5;

  let map = L.map('map').setView(fallbackCenter, fallbackZoom);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap'
  }).addTo(map);

  const lazyLoader = new LazyMarkerLoader(map, "${url}", {
    clusterOptions: {
      chunkedLoading: true,
      maxClusterRadius: 50,
    },
    debounceDelay: 500,
    autoLoad: true
  });

  lazyLoader.init();

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        let latitude = position.coords.latitude;
        let longitude = position.coords.longitude;
        map.setView([latitude, longitude], fallbackZoom);
      },
      () => {
        // Keep fallback center when geolocation is unavailable or denied
      },
      {
        enableHighAccuracy: false,
        timeout: 8000,
        maximumAge: 300000
      }
    );
  }
</script>