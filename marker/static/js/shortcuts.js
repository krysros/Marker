// Keyboard shortcuts for Marker app
// Handles: '/', '+', and '-' for search, add, and delete actions

function isInputActive() {
    const active = document.activeElement;
    return active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA' || active.isContentEditable);
}

function focusFirstSearch() {
    // Try to focus a search input first
    const searchInput = document.querySelector('input[type="search"], input[name*="search"], input[placeholder*="search" i]');
    if (searchInput) {
        searchInput.focus();
        if (searchInput.select) searchInput.select();
        return true;
    }
    // If no input, try to click a single search button (with icon)
    const searchBtns = document.querySelectorAll('a.btn,button.btn');
    const searchIconBtns = Array.from(searchBtns).filter(btn => {
        const icon = btn.querySelector('i.bi-search');
        return icon && btn.offsetParent !== null; // visible
    });
    if (searchIconBtns.length === 1) {
        searchIconBtns[0].click();
        return true;
    }
    // Fallback: try any visible button or link with title containing 'search'
    const searchTitleBtn = document.querySelector('button[title*="search" i], a[title*="search" i]');
    if (searchTitleBtn && searchTitleBtn.offsetParent !== null) {
        searchTitleBtn.click();
        return true;
    }
    return false;
}

function clickSingleButton(selector) {
    const btns = document.querySelectorAll(selector);
    if (btns.length === 1) {
        const btn = btns[0].closest('a,button');
        if (btn) {
            btn.click();
            return true;
        }
    }
    return false;
}

function setAccessKeyForSingle(selector, key) {
    const btns = document.querySelectorAll(selector);
    if (btns.length === 1) {
        const btn = btns[0].closest('a,button');
        if (btn) {
            btn.setAttribute('accesskey', key);
        }
    }
}

function handleShortcuts(event) {
    if (isInputActive()) return;

    // '/' focuses search
    if (event.key === '/' && !event.ctrlKey && !event.altKey && !event.metaKey) {
        if (focusFirstSearch()) {
            event.preventDefault();
        }
    }
    // '+' or Insert or NumpadAdd triggers single add button
    if ((event.key === '+' || event.key === 'Insert' || event.code === 'NumpadAdd')) {
        if (clickSingleButton('.btn.btn-success i.bi-plus-lg')) {
            event.preventDefault();
        }
    }
    // '-' or Delete or NumpadSubtract triggers single delete button
    if ((event.key === '-' || event.key === 'Delete' || event.code === 'NumpadSubtract')) {
        if (clickSingleButton('.btn.btn-danger i.bi-trash')) {
            event.preventDefault();
        }
    }
}

let shortcutsInitialized = false;
function setupShortcuts() {
    setAccessKeyForSingle('.btn.btn-success i.bi-plus-lg', '+');
    setAccessKeyForSingle('.btn.btn-danger i.bi-trash', '-');
    if (!shortcutsInitialized) {
        document.addEventListener('keydown', handleShortcuts);
        shortcutsInitialized = true;
    }
}

document.addEventListener('DOMContentLoaded', setupShortcuts);
document.body.addEventListener('htmx:afterSwap', function(e){
    setupShortcuts();
});
