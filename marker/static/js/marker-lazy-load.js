/**
 * Lazy Loading Markers for Leaflet Maps
 * 
 * This module provides lazy loading functionality for markers on leaflet maps.
 * Markers are loaded dynamically based on the current map viewport, improving
 * performance for maps with many markers.
 */

class LazyMarkerLoader {
  constructor(mapElement, dataUrl, options = {}) {
    this.map = mapElement;
    this.dataUrl = dataUrl;
    this.markers = L.markerClusterGroup({
      chunkedLoading: true,
      maxClusterRadius: 50,
      ...options.clusterOptions
    });
    
    this.loadedBounds = null;
    this.isLoading = false;
    this.markerCache = new Map();
    this.zoomThreshold = options.zoomThreshold || 12;
    this.debounceDelay = options.debounceDelay || 500;
    this.autoLoad = options.autoLoad !== false;
    
    this.debounceTimer = null;
    
    // Bootstrap color mapping (from Bootstrap 5.3)
    this.bootstrapColors = {
      'primary': '#0d6efd',
      'secondary': '#6c757d',
      'success': '#198754',
      'danger': '#dc3545',
      'warning': '#ffc107',
      'info': '#0dcaf0',
      'light': '#f8f9fa',
      'dark': '#212529'
    };
    
    // Add markers to map
    this.map.addLayer(this.markers);
  }
  
  /**
   * Initialize lazy loading by attaching map event listeners
   */
  init() {
    if (!this.autoLoad) return;
    
    // Load initial markers
    this.loadMarkers();
    
    // Listen for map movements
    this.map.on('moveend', () => this.onMapMoveEnd());
    this.map.on('zoomend', () => this.onMapMoveEnd());
  }
  
  /**
   * Handle map movement with debouncing
   */
  onMapMoveEnd() {
    clearTimeout(this.debounceTimer);
    this.debounceTimer = setTimeout(() => {
      this.loadMarkers();
    }, this.debounceDelay);
  }
  
  /**
   * Load markers for the current map bounds
   */
  async loadMarkers() {
    if (this.isLoading) return;
    
    const bounds = this.map.getBounds();
    const zoom = this.map.getZoom();
    
    // Skip loading if we haven't moved significantly
    if (this.loadedBounds && this._boundsSame(bounds, this.loadedBounds, zoom)) {
      return;
    }
    
    this.isLoading = true;
    this._showLoadingIndicator();
    
    try {
      const params = {
        north: bounds.getNorth(),
        south: bounds.getSouth(),
        east: bounds.getEast(),
        west: bounds.getWest(),
        zoom: zoom
      };
      
      const url = new URL(this.dataUrl, window.location.origin);
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.append(key, value);
      });
      
      const response = await fetch(url.toString());
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const items = await response.json();
      this._addMarkersToMap(items);
      
      this.loadedBounds = bounds;
    } catch (error) {
      console.error('Error loading markers:', error);
      this._showError('Failed to load markers');
    } finally {
      this.isLoading = false;
      this._hideLoadingIndicator();
    }
  }
  
  /**
   * Add markers to the map, avoiding duplicates
   */
  _addMarkersToMap(items) {
    for (const item of items) {
      if (item.latitude == null || item.longitude == null) continue;
      
      const cacheKey = `${item.id}`;
      if (this.markerCache.has(cacheKey)) continue;
      
      const title = this._createMarkerTitle(item);
      const marker = L.marker(
        new L.LatLng(item.latitude, item.longitude),
        { 
          title: this._stripHtml(title),
          ...this._getMarkerOptions(item)
        }
      );
      
      marker.bindPopup(title);
      this.markers.addLayer(marker);
      this.markerCache.set(cacheKey, marker);
    }
  }
  
  /**
   * Create HTML content for marker popup
   */
  _createMarkerTitle(item) {
    const title = `<a href="${item.url}"><b>${this._escapeHtml(item.name)}</b></a>`;
    const street = item.street ? `<br>${this._escapeHtml(item.street)}` : '';
    const city = item.city ? `<br>${this._escapeHtml(item.city)}` : '';
    const country = item.country ? `<br>${this._escapeHtml(item.country)}` : '';
    
    return title + street + city + country;
  }
  
  /**
   * Get marker options based on item properties
   */
  _getMarkerOptions(item) {
    const options = {};
    
    // Apply color if available
    if (item.color) {
      options.icon = L.icon({
        iconUrl: `data:image/svg+xml;base64,${this._getColoredMarkerSvg(item.color)}`,
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
      });
    }
    
    return options;
  }
  
  /**
   * Get base64 encoded colored marker SVG
   */
  _getColoredMarkerSvg(color) {
    // Map Bootstrap color names to hex values, or use as-is if hex color
    let hexColor = this.bootstrapColors[color] || color;
    
    // Validate that it's a valid color format
    if (!/^#[0-9a-f]{3}([0-9a-f]{3})?$/i.test(hexColor)) {
      // If not valid hex, use bootstrap primary as default
      hexColor = this.bootstrapColors['primary'];
    }
    
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 25 41">
      <path fill="${hexColor}" d="M12.5,0 C5.6,0 0,5.6 0,12.5 C0,20 12.5,41 12.5,41 C12.5,41 25,20 25,12.5 C25,5.6 19.4,0 12.5,0 Z" />
      <circle cx="12.5" cy="12.5" r="5" fill="white" />
    </svg>`;
    
    return btoa(svg);
  }
  
  /**
   * Check if bounds have changed significantly
   */
  _boundsSame(bounds1, bounds2, zoom) {
    if (!bounds2) return false;
    
    const tolerance = 1.0 / Math.pow(2, zoom);
    
    return Math.abs(bounds1.getNorth() - bounds2.getNorth()) < tolerance &&
           Math.abs(bounds1.getSouth() - bounds2.getSouth()) < tolerance &&
           Math.abs(bounds1.getEast() - bounds2.getEast()) < tolerance &&
           Math.abs(bounds1.getWest() - bounds2.getWest()) < tolerance;
  }
  
  /**
   * Show loading indicator
   */
  _showLoadingIndicator() {
    if (document.getElementById('marker-loading')) return;
    
    const loader = document.createElement('div');
    loader.id = 'marker-loading';
    loader.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Loading...</span></div> Loading markers...';
    loader.style.cssText = 'position: absolute; top: 10px; left: 50%; transform: translateX(-50%); z-index: 1000; background: white; padding: 10px 15px; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);';
    
    this.map.getContainer().parentElement.insertBefore(loader, this.map.getContainer());
  }
  
  /**
   * Hide loading indicator
   */
  _hideLoadingIndicator() {
    const loader = document.getElementById('marker-loading');
    if (loader) loader.remove();
  }
  
  /**
   * Show error message
   */
  _showError(message) {
    const error = document.createElement('div');
    error.innerHTML = `<div class="alert alert-danger" role="alert">${message}</div>`;
    error.style.cssText = 'position: absolute; top: 10px; left: 50%; transform: translateX(-50%); z-index: 1000; width: 90%; max-width: 500px;';
    
    this.map.getContainer().parentElement.insertBefore(error, this.map.getContainer());
    
    setTimeout(() => error.remove(), 5000);
  }
  
  /**
   * Escape HTML special characters
   */
  _escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
  
  /**
   * Strip HTML tags from text
   */
  _stripHtml(html) {
    const tmp = document.createElement('DIV');
    tmp.innerHTML = html;
    return tmp.textContent || tmp.innerText || '';
  }
  
  /**
   * Manually load markers at specified bounds
   */
  async loadAtBounds(bounds) {
    this.loadedBounds = null; // Force reload
    this.map.fitBounds(bounds);
    await this.loadMarkers();
  }
  
  /**
   * Clear all markers
   */
  clear() {
    this.markers.clearLayers();
    this.markerCache.clear();
    this.loadedBounds = null;
  }
  
  /**
   * Remove a specific marker by ID
   */
  removeMarker(id) {
    const cacheKey = `${id}`;
    const marker = this.markerCache.get(cacheKey);
    if (marker) {
      this.markers.removeLayer(marker);
      this.markerCache.delete(cacheKey);
    }
  }
  
  /**
   * Reload all markers
   */
  reload() {
    this.clear();
    this.loadMarkers();
  }
}
