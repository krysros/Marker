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
    this.itemCache = new Map();
    this.zoomThreshold = options.zoomThreshold || 12;
    this.debounceDelay = options.debounceDelay || 500;
    this.autoLoad = options.autoLoad !== false;
    this.csrfToken = options.csrfToken || '';
    
    this.debounceTimer = null;
    
    // Add markers to map
    this.map.addLayer(this.markers);
    this._attachPopupCheckboxHandler();
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
      await this._addMarkersToMap(items);

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
   * Add markers to the map in chunks, yielding between each chunk so the
   * browser can repaint and the progress bar stays responsive.
   */
  async _addMarkersToMap(items) {
    const newItems = items.filter(
      (item) =>
        item.latitude != null &&
        item.longitude != null &&
        !this.markerCache.has(`${item.id}`)
    );

    const total = newItems.length;
    if (total === 0) return;

    const CHUNK_SIZE = 50;

    for (let i = 0; i < total; i += CHUNK_SIZE) {
      const chunk = newItems.slice(i, i + CHUNK_SIZE);
      for (const item of chunk) {
        const cacheKey = `${item.id}`;
        const title = this._createMarkerTitle(item);
        const marker = L.marker(new L.LatLng(item.latitude, item.longitude), {
          title: this._stripHtml(title),
        });
        marker.bindPopup(title);
        this.markers.addLayer(marker);
        this.markerCache.set(cacheKey, marker);
        this.itemCache.set(cacheKey, item);
      }
      this._updateLoadingProgress(Math.min(i + CHUNK_SIZE, total), total);
      // Yield to the browser so it can repaint the progress bar
      await new Promise((resolve) => setTimeout(resolve, 0));
    }
  }
  
  /**
   * Create HTML content for marker popup
   */
  _createMarkerTitle(item) {
    const checkbox = this._createPopupCheckbox(item);
    const title = `<a href="${item.url}"><b>${this._escapeHtml(item.name)}</b></a>`;
    const details = [item.street, item.city, item.country]
      .filter((value) => value)
      .map((value) => this._escapeHtml(value))
      .join('<br>');

    const detailsHtml = details
      ? `<div class="marker-popup-details">${details}</div>`
      : '';

    if (checkbox) {
      return `<div style="display:flex;align-items:flex-start;gap:4px"><div style="flex-shrink:0;padding-top:2px">${checkbox}</div><div>${title}${detailsHtml}</div></div>`;
    }
    return `${title}${detailsHtml}`;
  }

  _createPopupCheckbox(item) {
    if (!item.check_url) return '';

    const checked = item.checked ? ' checked' : '';
    const checkUrl = this._escapeHtml(item.check_url);
    return `<input class="marker-popup-select me-2" type="checkbox" data-check-url="${checkUrl}" data-item-id="${item.id}" aria-label="Select item"${checked}>`;
  }

  _attachPopupCheckboxHandler() {
    this.map.getContainer().addEventListener('change', async (event) => {
      const checkbox = event.target;
      if (!checkbox.matches('input.marker-popup-select[data-check-url]')) {
        return;
      }

      const checkUrl = checkbox.dataset.checkUrl;
      if (!checkUrl) {
        return;
      }

      const previousChecked = !checkbox.checked;
      checkbox.disabled = true;
      try {
        const headers = {
          'X-Requested-With': 'XMLHttpRequest'
        };
        if (this.csrfToken) {
          headers['X-CSRF-Token'] = this.csrfToken;
        }

        const response = await fetch(checkUrl, {
          method: 'POST',
          headers
        });

        if (!response.ok) {
          throw new Error(`HTTP error ${response.status}`);
        }

        const result = await response.json();
        if (result && typeof result.checked === 'boolean') {
          checkbox.checked = result.checked;
        }
        const itemId = checkbox.dataset.itemId;
        if (itemId) {
          const item = this.itemCache.get(itemId);
          if (item) {
            item.checked = checkbox.checked;
            const marker = this.markerCache.get(itemId);
            if (marker) {
              marker.setPopupContent(this._createMarkerTitle(item));
            }
          }
        }
      } catch (error) {
        checkbox.checked = previousChecked;
        console.error('Error toggling marker selection:', error);
      } finally {
        checkbox.disabled = false;
      }
    });
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
   * Show loading indicator with progress bar
   */
  _showLoadingIndicator() {
    const el = document.getElementById('marker-loading');
    if (el) {
      const bar = document.getElementById('marker-loading-bar');
      const label = document.getElementById('marker-loading-label');
      if (bar) {
        bar.style.width = '0%';
        bar.style.transition = 'none';
        bar.setAttribute('aria-valuenow', 0);
        bar.classList.add('progress-bar-striped', 'progress-bar-animated');
      }
      if (label) label.textContent = 'Loading markers…';
      el.removeAttribute('hidden');
    }
  }

  /**
   * Update loading progress
   */
  _updateLoadingProgress(current, total) {
    const bar = document.getElementById('marker-loading-bar');
    const label = document.getElementById('marker-loading-label');
    if (!bar || !label) return;
    const pct = total > 0 ? Math.round((current / total) * 100) : 0;
    bar.style.width = pct + '%';
    bar.setAttribute('aria-valuenow', pct);
    label.textContent = `Loaded ${current} / ${total} markers`;
  }

  /**
   * Hide loading indicator
   */
  _hideLoadingIndicator() {
    // Small delay so the completed bar is visible before hiding
    setTimeout(() => {
      const el = document.getElementById('marker-loading');
      if (el) el.setAttribute('hidden', '');
    }, 600);
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
