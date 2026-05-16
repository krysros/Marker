(function () {
  function syncTableSelectAll(table) {
    const selectAll = table.querySelector('thead input.marker-select-all[type="checkbox"]');
    if (!selectAll) {
      return;
    }

    const rowCheckboxes = table.querySelectorAll(
      'tbody input.marker-select-item[type="checkbox"]'
    );

    const totalRows = rowCheckboxes.length;

    if (totalRows === 0) {
      selectAll.checked = false;
      selectAll.indeterminate = false;
      return;
    }

    let checkedCount = 0;
    rowCheckboxes.forEach((checkbox) => {
      if (checkbox.checked) {
        checkedCount += 1;
      }
    });

    if (checkedCount === 0) {
      selectAll.checked = false;
      selectAll.indeterminate = false;
      return;
    }

    if (checkedCount === totalRows) {
      selectAll.checked = true;
      selectAll.indeterminate = false;
      return;
    }

    selectAll.checked = false;
    selectAll.indeterminate = true;
  }

  function syncAllSelectAllCheckboxes() {
    const tables = document.querySelectorAll('table');
    tables.forEach(syncTableSelectAll);
  }

  function tableFromEvent(event) {
    const candidates = [
      event.target,
      event.detail && event.detail.elt,
      event.detail && event.detail.target,
    ];

    for (const candidate of candidates) {
      if (candidate instanceof Element) {
        const table = candidate.closest('table');
        if (table) {
          return table;
        }
      }
    }

    return null;
  }

  document.addEventListener('change', (event) => {
    const target = event.target;
    if (!(target instanceof HTMLInputElement)) {
      return;
    }

    if (target.matches('tbody input.marker-select-item[type="checkbox"]')) {
      const table = target.closest('table');
      if (table) {
        syncTableSelectAll(table);
      }
      return;
    }

    if (target.matches('thead input.marker-select-all[type="checkbox"]')) {
      target.indeterminate = false;
    }
  });

  document.addEventListener('DOMContentLoaded', syncAllSelectAllCheckboxes);
  document.addEventListener('htmx:after:swap', (event) => {
    const table = tableFromEvent(event);
    if (table) {
      syncTableSelectAll(table);
      return;
    }

    syncAllSelectAllCheckboxes();
  });
})();
