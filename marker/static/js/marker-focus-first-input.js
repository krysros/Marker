// marker-focus-first-input.js
// Sets focus to the first field of each form after page or fragment (htmx) load

function focusFirstInput(root) {
  const scope = root && root.querySelectorAll ? root : document;
  // Only search visible forms
  const forms = scope.querySelectorAll('form');
  forms.forEach(form => {
    // Find the first visible input, select, or textarea that is not hidden or disabled
    const first = form.querySelector('input:not([type=hidden]):not([disabled]), select:not([disabled]), textarea:not([disabled])');
    if (first) {
      first.focus();
    }
  });
}

document.addEventListener('DOMContentLoaded', function() {
  focusFirstInput(document);
});

document.body.addEventListener('htmx:afterSwap', function(e) {
  focusFirstInput(e.target);
});
