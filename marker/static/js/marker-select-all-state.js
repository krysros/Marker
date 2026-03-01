(function () {
  function syncTableSelectAll(table) {
    const selectAll = table.querySelector('thead input.marker-select-all[type="checkbox"]');
    if (!selectAll) {
      return;
    }

    const rowCheckboxes = Array.from(
      table.querySelectorAll('tbody input.marker-select-item[type="checkbox"]')
    );

    if (rowCheckboxes.length === 0) {
      selectAll.indeterminate = false;
      return;
    }

    const checkedCount = rowCheckboxes.filter((checkbox) => checkbox.checked).length;

    if (checkedCount === 0) {
      selectAll.checked = false;
      selectAll.indeterminate = false;
      return;
    }

    if (checkedCount === rowCheckboxes.length) {
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
  document.body.addEventListener('htmx:afterSwap', syncAllSelectAllCheckboxes);
  document.body.addEventListener('htmx:afterSettle', syncAllSelectAllCheckboxes);
})();
