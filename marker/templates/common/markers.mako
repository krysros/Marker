<div id="marker-loading" hidden class="mt-2">
  <div class="progress" style="height:6px">
    <div id="marker-loading-bar" class="progress-bar progress-bar-striped progress-bar-animated"
         role="progressbar" style="width:0%" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>
  </div>
  <div id="marker-loading-label" class="text-muted small mt-1">Loading markers…</div>
</div>
<script src="${request.static_url('marker:static/js/marker-lazy-load.js')}"></script>
<script>
  const fallbackCenter = [52.2297, 21.0122];
  const fallbackZoom = 5;

  // Function to adjust the map height to fit the remaining window height
  function resizeMap() {
    const mapEl = document.getElementById('map');
    if (mapEl) {
      const rect = mapEl.getBoundingClientRect();
      const top = rect.top;
      
      // Calculate height of the footer
      const footer = document.querySelector('footer');
      const footerHeight = footer ? footer.offsetHeight : 0;
      
      // Available height is viewport height minus map top offset, footer height, and some margins
      const margin = 20; // safe margin
      const availableHeight = window.innerHeight - top - footerHeight - margin;
      
      // We set minimum height to 300px to keep it usable on very small screens/mobile
      mapEl.style.height = Math.max(availableHeight, 300) + 'px';
    }
  }

  // Call resizeMap before initializing Leaflet so it has the correct height initially!
  resizeMap();

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

  // Resize and load event listeners to ensure map size is always accurate
  window.addEventListener('resize', () => {
    resizeMap();
    if (map && map.invalidateSize) {
      map.invalidateSize();
    }
  });

  window.addEventListener('load', () => {
    resizeMap();
    if (map && map.invalidateSize) {
      map.invalidateSize();
    }
  });

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