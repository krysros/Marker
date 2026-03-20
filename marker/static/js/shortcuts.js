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


function isHomePage() {
    // Simple check: body has class 'home' or path is '/'
    return window.location.pathname === '/' || document.body.classList.contains('home');
}

function openAddSelectModal() {
    const modal = document.getElementById('addSelectModal');
    if (!modal) return;
    const bsModal = bootstrap.Modal.getOrCreateInstance(modal);
    bsModal.show();
    // Focus first item
    const list = document.getElementById('addSelectList');
    if (list) {
        const items = list.querySelectorAll('.list-group-item');
        if (items.length) items[0].focus();
    }
}

function handleAddSelectModalKeys(e) {
    const modal = document.getElementById('addSelectModal');
    if (!modal || !modal.classList.contains('show')) return;
    const list = document.getElementById('addSelectList');
    const items = Array.from(list.querySelectorAll('.list-group-item'));
    let idx = items.findIndex(item => item === document.activeElement);
    if (e.key >= '1' && e.key <= '3') {
        const i = parseInt(e.key, 10) - 1;
        if (items[i]) {
            window.location.href = items[i].dataset.url;
            e.preventDefault();
        }
    } else if (e.key === 'ArrowDown') {
        if (idx < items.length - 1) {
            items[idx + 1].focus();
            e.preventDefault();
        }
    } else if (e.key === 'ArrowUp') {
        if (idx > 0) {
            items[idx - 1].focus();
            e.preventDefault();
        }
    } else if (e.key === 'Enter') {
        if (idx >= 0) {
            window.location.href = items[idx].dataset.url;
            e.preventDefault();
        }
    } else if (e.key === 'Escape') {
        bootstrap.Modal.getOrCreateInstance(modal).hide();
        e.preventDefault();
    }
}

function openSearchSelectModal() {
    const modal = document.getElementById('searchSelectModal');
    if (!modal) return;
    const bsModal = bootstrap.Modal.getOrCreateInstance(modal);
    bsModal.show();
    // Focus first item
    const list = document.getElementById('searchSelectList');
    if (list) {
        const items = list.querySelectorAll('.list-group-item');
        if (items.length) items[0].focus();
    }
}

function handleSearchSelectModalKeys(e) {
    const modal = document.getElementById('searchSelectModal');
    if (!modal || !modal.classList.contains('show')) return;
    const list = document.getElementById('searchSelectList');
    const items = Array.from(list.querySelectorAll('.list-group-item'));
    let idx = items.findIndex(item => item === document.activeElement);
    if (e.key >= '1' && e.key <= '5') {
        const i = parseInt(e.key, 10) - 1;
        if (items[i]) {
            window.location.href = items[i].dataset.url;
            e.preventDefault();
        }
    } else if (e.key === 'ArrowDown') {
        if (idx < items.length - 1) {
            items[idx + 1].focus();
            e.preventDefault();
        }
    } else if (e.key === 'ArrowUp') {
        if (idx > 0) {
            items[idx - 1].focus();
            e.preventDefault();
        }
    } else if (e.key === 'Enter') {
        if (idx >= 0) {
            window.location.href = items[idx].dataset.url;
            e.preventDefault();
        }
    } else if (e.key === 'Escape') {
        bootstrap.Modal.getOrCreateInstance(modal).hide();
        e.preventDefault();
    }
}

function handleShortcuts(event) {
    if (isInputActive()) return;
    // 1-5 on homepage: quick navigation to main sections (company, project, tag, contact, comment)
    // Only trigger if neither search nor add modal is open
    const searchModal = document.getElementById('searchSelectModal');
    const addModal = document.getElementById('addSelectModal');
    const modalOpen = (searchModal && searchModal.classList.contains('show')) || (addModal && addModal.classList.contains('show'));
    if (isHomePage() && !modalOpen && !event.ctrlKey && !event.altKey && !event.metaKey && event.key >= '1' && event.key <= '5') {
        const urls = [
            '/company',  // company_all
            '/project',  // project_all
            '/tag',      // tag_all
            '/contact',  // contact_all
            '/comment'   // comment_all
        ];
        const idx = parseInt(event.key, 10) - 1;
        if (urls[idx]) {
            window.location.href = urls[idx];
            event.preventDefault();
            return;
        }
    }
    // '*' toggles star in company/project star views
    if ((event.key === '*' || event.key === 'NumpadMultiply') && !event.ctrlKey && !event.altKey && !event.metaKey) {
        // Try to click the single visible star button
        if (clickSingleButton('.btn.btn-primary i.bi-star, .btn.btn-primary i.bi-star-fill')) {
            event.preventDefault();
            return;
        }
    }
    // Home key redirects to homepage
    if (event.key === 'Home' && !event.ctrlKey && !event.altKey && !event.metaKey) {
        // The homepage is always at '/'
        window.location.href = '/';
        event.preventDefault();
        return;
    }
    // '/' opens search modal or focuses search input
    if (event.key === '/' && !event.ctrlKey && !event.altKey && !event.metaKey) {
        if (isHomePage()) {
            openSearchSelectModal();
            event.preventDefault();
        } else {
            if (focusFirstSearch()) {
                event.preventDefault();
            }
        }
    }
    // '+' or Insert or NumpadAdd opens add modal or triggers add button
    if ((event.key === '+' || event.key === 'Insert' || event.code === 'NumpadAdd')) {
        if (isHomePage()) {
            openAddSelectModal();
            event.preventDefault();
        } else {
            if (clickSingleButton('.btn.btn-success i.bi-plus-lg')) {
                event.preventDefault();
            }
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
    setAccessKeyForSingle('.btn.btn-primary i.bi-star, .btn.btn-primary i.bi-star-fill', '*');
    if (!shortcutsInitialized) {
        document.addEventListener('keydown', handleShortcuts);
        shortcutsInitialized = true;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    setupShortcuts();
    // Modal search selection: click and keyboard
    const searchList = document.getElementById('searchSelectList');
    if (searchList) {
        searchList.addEventListener('click', function(e) {
            const item = e.target.closest('.list-group-item');
            if (item && item.dataset.url) {
                window.location.href = item.dataset.url;
            }
        });
        // Make items focusable
        searchList.querySelectorAll('.list-group-item').forEach(item => {
            item.tabIndex = 0;
        });
    }
    const addList = document.getElementById('addSelectList');
    if (addList) {
        addList.addEventListener('click', function(e) {
            const item = e.target.closest('.list-group-item');
            if (item && item.dataset.url) {
                window.location.href = item.dataset.url;
            }
        });
        addList.querySelectorAll('.list-group-item').forEach(item => {
            item.tabIndex = 0;
        });
    }
    document.addEventListener('keydown', handleSearchSelectModalKeys, true);
    document.addEventListener('keydown', handleAddSelectModalKeys, true);
});
document.body.addEventListener('htmx:afterSwap', function(e){
    setupShortcuts();
});
document.body.addEventListener('htmx:afterSwap', function(e){
    setupShortcuts();
});
