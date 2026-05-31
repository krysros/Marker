// marker-select-all-state.js - Alpine.js powered select-all sync
// Automatically handles select-all/item checkbox syncing and indeterminate state

document.addEventListener('alpine:init', () => {
    Alpine.directive('select-all-table', (el) => {
        const sync = () => {
            const selectAll = el.querySelector('thead input.marker-select-all[type="checkbox"]');
            if (!selectAll) return;

            const items = [...el.querySelectorAll('tbody input.marker-select-item[type="checkbox"]')];
            const checkedCount = items.filter(cb => cb.checked).length;

            if (items.length === 0) {
                selectAll.checked = false;
                selectAll.indeterminate = false;
            } else if (checkedCount === 0) {
                selectAll.checked = false;
                selectAll.indeterminate = false;
            } else if (checkedCount === items.length) {
                selectAll.checked = true;
                selectAll.indeterminate = false;
            } else {
                selectAll.checked = false;
                selectAll.indeterminate = true;
            }
        };

        // Listen for changes inside this table
        el.addEventListener('change', (e) => {
            const target = e.target;
            
            // If individual item clicked, sync header checkbox
            if (target.matches('tbody input.marker-select-item[type="checkbox"]')) {
                sync();
            }

            // If header select-all clicked, toggle all body checkboxes
            if (target.matches('thead input.marker-select-all[type="checkbox"]')) {
                target.indeterminate = false;
                const isChecked = target.checked;
                el.querySelectorAll('tbody input.marker-select-item[type="checkbox"]').forEach(cb => {
                    if (cb.checked !== isChecked) {
                        cb.checked = isChecked;
                        cb.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                });
            }
        });

        // Sync initially
        sync();

        // Automatically sync on any htmx swaps within this table
        el.addEventListener('htmx:afterSwap', sync);
    });

    // Automatically apply x-select-all-table directive to all tables containing select-all checkboxes
    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('table').forEach(table => {
            if (table.querySelector('.marker-select-all')) {
                table.setAttribute('x-select-all-table', '');
            }
        });
    });

    // Also apply to any tables loaded dynamically by htmx
    document.addEventListener('htmx:afterSwap', (e) => {
        const target = e.target;
        const tables = target.tagName === 'TABLE' ? [target] : target.querySelectorAll('table');
        tables.forEach(table => {
            if (table.querySelector('.marker-select-all') && !table.hasAttribute('x-select-all-table')) {
                table.setAttribute('x-select-all-table', '');
                // Boot directive for dynamically added element
                Alpine.initializeElements(table);
            }
        });
    });
});
