<script src="${request.static_url('marker:static/js/marker-lazy-load.js')}"></script>
<script>
  const fallbackCenter = [52.2297, 21.0122];
  const fallbackZoom = 5;

  let map = L.map('map').setView(fallbackCenter, fallbackZoom);
  let userInteractedWithMap = false;

  const markUserInteraction = () => {
    userInteractedWithMap = true;
  };

  map.on('movestart', markUserInteraction);
  map.on('zoomstart', markUserInteraction);
  map.on('dragstart', markUserInteraction);

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
    autoLoad: true,
    csrfToken: "${get_csrf_token()}"
  });

  lazyLoader.init();

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        if (userInteractedWithMap) {
          return;
        }
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