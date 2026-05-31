// marker-website-autofill.js - Alpine.js powered form autofill
// Dynamically fetches and autofills address/company data from a website URL

document.addEventListener('alpine:init', () => {
    Alpine.data('autofillForm', () => ({
        loading: false,
        async triggerAutofill(triggerEl) {
            const group = triggerEl.closest('.input-group');
            const input = group?.querySelector('input[data-website-autofill-url]');
            const form = input?.form;
            if (!input || !form || this.loading) return;

            const website = (input.value || '').trim();
            const autofillUrl = input.dataset.websiteAutofillUrl;
            const subdivisionUrl = input.dataset.subdivisionUrl;

            this.loading = true;
            try {
                if (!website) {
                    this.setFields(form, {});
                    await this.syncSubdivision(form, subdivisionUrl, '', '');
                    return;
                }

                const url = new URL(autofillUrl, window.location.origin);
                url.searchParams.set('website', website);
                const res = await fetch(url, {
                    headers: {
                        'Accept': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                if (res.ok) {
                    const payload = await res.json();
                    const fields = payload?.fields || {};
                    this.setFields(form, fields);
                    await this.syncSubdivision(form, subdivisionUrl, fields.country || '', fields.subdivision || '');
                }
            } catch (err) {
                console.error('Autofill request failed:', err);
            } finally {
                this.loading = false;
            }
        },
        setFields(form, fields) {
            const managed = ["name", "street", "postcode", "city", "country", "NIP", "REGON", "KRS"];
            managed.forEach(name => {
                const el = form.elements[name];
                if (el) el.value = fields[name] || '';
            });
        },
        async syncSubdivision(form, subdivisionUrl, country, val) {
            const subEl = form.elements['subdivision'];
            if (!subEl) return;
            if (!subdivisionUrl) {
                subEl.value = val || '';
                return;
            }
            try {
                const url = new URL(subdivisionUrl, window.location.origin);
                url.searchParams.set('country', country);
                const res = await fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
                if (res.ok) {
                    subEl.innerHTML = await res.text();
                    subEl.value = val || '';
                }
            } catch {
                subEl.value = val || '';
            }
        }
    }));
});

// Auto-initialize form autofill with Alpine.js
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('input[data-website-autofill-url]').forEach(input => {
        const form = input.form;
        if (form && !form.hasAttribute('x-data')) {
            form.setAttribute('x-data', 'autofillForm');
            const trigger = form.querySelector('[data-website-autofill-trigger]');
            if (trigger) {
                trigger.setAttribute('x-on:click', 'triggerAutofill($el)');
                trigger.setAttribute('x-bind:disabled', 'loading');
                
                const icon = trigger.querySelector('[data-website-autofill-icon]');
                if (icon) icon.setAttribute('x-show', '!loading');
                
                const spinner = trigger.querySelector('[data-website-autofill-spinner]');
                if (spinner) {
                    spinner.setAttribute('x-show', 'loading');
                    spinner.classList.remove('d-none'); // Allow Alpine x-show to control visibility
                }
            }
            Alpine.initializeElements(form);
        }
    });
});
