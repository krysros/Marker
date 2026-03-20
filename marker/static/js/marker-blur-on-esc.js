// marker-blur-on-esc.js
// Removes focus from form fields on Escape key, so global shortcuts work

document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape' && !e.ctrlKey && !e.altKey && !e.metaKey) {
    const active = document.activeElement;
    if (active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA' || active.tagName === 'SELECT' || active.isContentEditable)) {
      active.blur();
    }
  }
});
