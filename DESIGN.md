---
version: alpha
name: Marker
description: B2B CRM application for managing companies, projects, contacts and tags.
colors:
  primary: "#0d6efd"
  secondary: "#6c757d"
  success: "#198754"
  danger: "#dc3545"
  warning: "#ffc107"
  info: "#0dcaf0"
  surface: "#ffffff"
  surface-alt: "#f8f9fa"
  on-surface: "#212529"
  on-surface-muted: "#6c757d"
  border: "#dee2e6"
typography:
  headline-lg:
    fontFamily: system-ui, -apple-system, sans-serif
    fontSize: 1.75rem
    fontWeight: 500
    lineHeight: 1.2
  headline-md:
    fontFamily: system-ui, -apple-system, sans-serif
    fontSize: 1.5rem
    fontWeight: 500
    lineHeight: 1.2
  headline-sm:
    fontFamily: system-ui, -apple-system, sans-serif
    fontSize: 1.25rem
    fontWeight: 500
    lineHeight: 1.2
  body-lg:
    fontFamily: system-ui, -apple-system, sans-serif
    fontSize: 1rem
    fontWeight: 400
    lineHeight: 1.5
  body-md:
    fontFamily: system-ui, -apple-system, sans-serif
    fontSize: 0.875rem
    fontWeight: 400
    lineHeight: 1.5
  label-md:
    fontFamily: system-ui, -apple-system, sans-serif
    fontSize: 0.875rem
    fontWeight: 600
    lineHeight: 1
  caption:
    fontFamily: system-ui, -apple-system, sans-serif
    fontSize: 0.75rem
    fontWeight: 400
    lineHeight: 1.4
  code:
    fontFamily: SFMono-Regular, Menlo, Monaco, Consolas, monospace
    fontSize: 0.875rem
    fontWeight: 400
    lineHeight: 1.5
rounded:
  none: 0
  sm: 4px
  md: 6px
  lg: 8px
  full: 9999px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  xxl: 48px
  gutter: 24px
  section: 32px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.surface}"
    rounded: "{rounded.md}"
    padding: 6px 12px
    typography: "{typography.label-md}"
  button-primary-hover:
    backgroundColor: "#0b5ed7"
    textColor: "{colors.surface}"
  button-secondary:
    backgroundColor: "{colors.secondary}"
    textColor: "{colors.surface}"
    rounded: "{rounded.md}"
    padding: 6px 12px
  button-secondary-hover:
    backgroundColor: "#5c636a"
    textColor: "{colors.surface}"
  button-success:
    backgroundColor: "{colors.success}"
    textColor: "{colors.surface}"
    rounded: "{rounded.md}"
    padding: 6px 12px
  button-danger:
    backgroundColor: "{colors.danger}"
    textColor: "{colors.surface}"
    rounded: "{rounded.md}"
    padding: 6px 12px
  button-warning:
    backgroundColor: "{colors.warning}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.md}"
    padding: 6px 12px
  button-sm:
    padding: 4px 8px
    typography: "{typography.body-md}"
  card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.lg}"
    padding: 16px
  card-header:
    backgroundColor: "{colors.surface-alt}"
    textColor: "{colors.on-surface}"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.md}"
    padding: 6px 12px
  input-focus:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
  badge:
    rounded: "{rounded.full}"
    padding: 4px 8px
    typography: "{typography.caption}"
  navbar:
    backgroundColor: "{colors.surface-alt}"
    textColor: "{colors.on-surface}"
  alert-info:
    backgroundColor: "#cff4fc"
    textColor: "#055160"
  alert-success:
    backgroundColor: "#d1e7dd"
    textColor: "#0a3622"
  alert-danger:
    backgroundColor: "#f8d7da"
    textColor: "#58151c"
  alert-warning:
    backgroundColor: "#fff3cd"
    textColor: "#664d03"
---

## Overview

Marker is a B2B CRM for construction-industry professionals — used to track
companies, projects, contacts, and tags. The interface is dense and data-heavy:
lists, filterable tables, detail cards, and inline forms.

The visual language is **functional and restrained**. Bootstrap 5 provides the
structural foundation. Custom styling is minimal — the app follows Bootstrap's
default token system and avoids custom CSS except where layout, transitions, or
component glue require it. Dark mode is supported via Bootstrap's `data-bs-theme`
attribute set on `<html>`.

The tech stack for all UI is fixed:
- **Mako** — server-side HTML templates. All UI is Mako; never emit raw HTML
  from Python views.
- **Bootstrap 5.3** — layout, components, and utilities.
- **Bootstrap Icons** — icon font via `<i class="bi bi-{name}"></i>`.
- **htmx 2** — progressive enhancement for dynamic interactions.

## Colors

The palette is Bootstrap 5's semantic color system with no custom brand overrides.
This makes the app automatically adapt to Bootstrap theme updates and dark-mode
without extra work.

- **Primary (`#0d6efd`):** Navigation links, primary action buttons, active states.
- **Secondary (`#6c757d`):** Supplementary actions, muted badges, helper buttons.
- **Success (`#198754`):** Add/create actions; positive confirmation badges.
- **Danger (`#dc3545`):** Delete/destructive actions; error states.
- **Warning (`#ffc107`):** Edit actions; caution states.
- **Info (`#0dcaf0`):** Search criteria banners; informational alerts.
- **Surface (`#ffffff`):** Card backgrounds, input backgrounds.
- **Surface-alt (`#f8f9fa`):** Page body, card headers, navbar background.
- **On-surface (`#212529`):** Primary text.
- **On-surface-muted (`#6c757d`):** Secondary text, captions, placeholder labels.
- **Border (`#dee2e6`):** Dividers, card borders, table cell borders.

Color assignment is role-based, not decorative. Do not use `primary` for destructive
actions, or `danger` for anything other than deletes and errors.

## Typography

System UI font stack — no Google Fonts or external font dependencies. Bootstrap
provides the full type scale via `<h1>`–`<h6>`, `.fs-*` utilities and `.lead`.

Concrete usage:
- Page titles: `<h2>` with `<i class="bi bi-...">` icon prefix.
- Section headings inside cards: `<div class="card-header">` with icon + label.
- Numeric counts (badges): `<span class="badge bg-secondary">` — always a `<span>`, never an `<a>`.
- Code values (keyboard shortcuts): `<kbd>` element.
- Timestamps / metadata: `<small>` or `text-muted` utility class.
- Captions / helper text: `<small class="text-muted">`.

Do not introduce non-system fonts. Do not use inline `style="font-*"` attributes.

## Layout

Bootstrap's fluid container at a single breakpoint: `<div class="container">` is
the top-level page wrapper, defined once in `base/layout.mako`. All page content
flows inside this container.

Spacing follows Bootstrap's `m-*` / `p-*` scale (step = 4px × multiplier):
- Between major sections on a page: `mt-4 mb-4` (`32px`).
- Between closely related elements: `gap-2` in flex containers (`8px`).
- Card internal padding: Bootstrap default (`16px`).
- Form groups: `mb-3` between fields.

Action button rows use `<div class="hstack gap-2 mb-4 d-flex flex-wrap">` as the
standard pattern. Icons and filter controls go left (`me-auto`); sort/order
dropdowns and export buttons go right.

For all paginated list views, the pattern is:
1. Page title `<h2>` with counter badge and action buttons (`float-end`).
2. Horizontal `<hr>`.
3. Filter / sort control row (`hstack`).
4. Search-criteria alert (if active).
5. Table or card list.
6. Infinite-scroll sentinel (`hx-get` + `hx-trigger="intersect once"`).

Column structure inside cards: `.row > .col` (Bootstrap's auto grid). Use `.row.g-3`
when columns should have consistent gutters.

Do not use `position: fixed` or `position: absolute` for anything other than the
fixed-top navbar (already defined in `base/navbar.mako`). Do not add a sidebar.

## Elevation & Depth

Depth is conveyed entirely through tonal layers and borders, not box shadows.
Bootstrap cards (`card`, `card-header`, `card-body`) are the only elevated surface.
The page background (`surface-alt`) is one tone lighter than cards (`surface`).

`card-header` uses `bg-body-tertiary` (mapped to `surface-alt`) to visually
separate the heading from the card body without a shadow. No `box-shadow` overrides.

Modals use Bootstrap's default overlay (`modal-backdrop`) with no custom
shadow changes.

## Shapes

All interactive elements use Bootstrap's default corner radius (`rounded.md` = 6px).
Badges use `rounded-pill` (`rounded.full`). Do not mix sharp and rounded corners
within the same UI region.

The `rounded` token scale maps directly to Bootstrap's `.rounded-*` utility classes:
- `rounded.sm` → `.rounded-1`
- `rounded.md` → `.rounded-2` (Bootstrap default — omit the class)
- `rounded.lg` → `.rounded-3`
- `rounded.full` → `.rounded-pill`

## Components

### Template Architecture

All reusable UI fragments are Mako `<%def>` macros inside `marker/templates/common/`.
Use `<%namespace>` to import them; do not copy-paste component markup across templates.

**Existing reusable macros:**

| File | Macros | Purpose |
|------|--------|---------|
| `common/button.mako` | `a()`, `button()`, `del_card()`, `dropdown_sort()`, `dropdown_order()` | Buttons and action dropdowns |
| `common/checkbox.mako` | `checkbox()`, `select_all()` | htmx-wired selection checkboxes |
| `common/pills.mako` | `pills()` | Nav-pill tab bars with live htmx counters |
| `common/search_criteria.mako` | *(included directly)* | Active filter summary alert |
| `common/markers.mako` | *(map-related)* | Leaflet map marker helpers |
| `common/activity_form.mako` | *(activity form)* | Inline activity entry |
| `common/subdivision.mako` | *(subdivision select)* | Subdivision dropdown helper |

### Buttons

Use the `button.a()` macro for `<a>` links styled as buttons.
Use `button.button()` for htmx POST actions (auto-adds CSRF header and confirm dialog).
Use `button.del_card()` for delete actions that remove a card from the DOM via `hx-target="closest .card" hx-swap="outerHTML swap:1s"`.

Button color semantics:
- `success` — add / create
- `warning` — edit
- `danger` — delete
- `primary` — navigate to search / primary view
- `secondary` — secondary navigation (map, uptime, export)

Button size: omit `size` param for default; pass `size='sm'` for inline actions
inside tables or card bodies.

### Cards

Standard card pattern:
```html
<div class="card mt-4 mb-4">
  <div class="card-header">
    <i class="bi bi-{icon}"></i> ${_("Section title")}
  </div>
  <div class="card-body">
    ...
  </div>
</div>
```

For cards in a list that can be deleted with htmx, wrap the entire card in the
`del_card()` button target: the button macro uses `hx-target="closest .card"`.

### Tables

All list tables follow this structure:
```html
<div class="table-responsive">
  <table class="table table-hover align-middle">
    <thead>
      <tr>...</tr>
    </thead>
    <tbody id="{entity}-list">
      ...rows...
    </tbody>
  </table>
</div>
```

The `tbody` must have a stable `id` matching the pattern `{entity}-list`
(e.g., `company-list`, `project-list`). htmx infinite scroll appends to this id.

Infinite scroll sentinel goes immediately after the table:
```html
% if next_page:
<div hx-get="${next_page}"
     hx-trigger="intersect once"
     hx-target="#company-list"
     hx-swap="beforeend">
</div>
% endif
```

### Forms

WTForms rendered in Mako. Canonical field pattern:
```html
<div class="mb-3">
  <label for="${form.field_name.id}" class="form-label">${form.field_name.label.text}</label>
  ${form.field_name(class_="form-control", ...)}
  % if form.field_name.errors:
    % for error in form.field_name.errors:
      <div class="invalid-feedback d-block">${error}</div>
    % endfor
  % endif
</div>
```

Submit buttons: `<button type="submit" class="btn btn-primary">`.
Cancel links: `<a href="..." class="btn btn-secondary">`.

All forms that mutate state must include a CSRF token:
```html
<input type="hidden" name="csrf_token" value="${get_csrf_token()}">
```

### Navbar

Defined once in `base/navbar.mako`. Do not duplicate navigation elements on
individual pages. The navbar is `fixed-top`, hence the `padding-top: 6rem` rule
in `static/css/style.css`.

### Flash Messages

Defined in `base/flash_messages.mako` (included in `base/layout.mako`). Flash
messages format: `"{alert_type}:{message}"` (e.g., `"success:Company saved."`).
Do not emit HTML in flash message text — it is rendered without escaping via `| n`
but must only contain safe trusted content from the server.

### Badges / Counters

Numeric counts in page headings:
```html
<span class="badge bg-secondary">${counter}</span>
```

Live-updating counters in nav pills use htmx:
```html
<div hx-get="${count_url}" hx-trigger="companyEvent from:body">
  ${init_value}
</div>
```

Trigger events are fired server-side via `HX-Trigger` response headers when
mutations occur (e.g., `htmx_refresh_response()` from `marker.views`).

### Alerts

Use Bootstrap's contextual alert classes: `alert-info`, `alert-success`,
`alert-warning`, `alert-danger`. Always include `role="alert"`. Add
`alert-dismissible fade show` and a `.btn-close` button for persistent banners.

## htmx Usage

htmx is the primary mechanism for all partial-page updates. Prefer htmx over
full-page navigation wherever the change is incremental, well-contained, and does
not degrade readability or performance.

### When to use htmx

| Use case | htmx pattern |
|----------|-------------|
| Infinite scroll / pagination | `hx-get` + `hx-trigger="intersect once"` + `hx-swap="beforeend"` on `tbody` |
| Checkbox selection (single item) | `hx-post` + `hx-trigger="click"` + `hx-swap="none"` |
| Select-all checkbox | `hx-post` + `hx-vals='js:{checked: event.target.checked}'` + `hx-swap="none"` |
| Delete a card from a list | `hx-post` + `hx-target="closest .card"` + `hx-swap="outerHTML swap:1s"` |
| Live counter refresh | `hx-get` + `hx-trigger="{customEvent} from:body"` |
| Star toggle | `hx-post` + `hx-swap="outerHTML"` targeting the star button itself |
| Website autofill | `hx-post` + `hx-target` targeting the form fields container |
| Inline form submission (activity) | `hx-post` + `hx-target` + `hx-swap="beforeend"` or `outerHTML` |

### When NOT to use htmx

- Full form submits (add / edit entity): use standard POST → redirect (PRG pattern).
- Navigation between pages: use `<a href="...">`.
- Complex form validation requiring server round-trips on every keystroke.
- Any interaction where a full-page reload is simpler and equally fast.

### htmx conventions

- Always include the CSRF token via `hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'`
  on every `hx-post`, `hx-put`, `hx-delete` request.
- Use `hx-confirm='${_("Are you sure?")}'` on destructive actions.
- Swap animations use the `htmx-swapping` CSS class defined in `style.css`:
  `opacity: 0; transition: opacity 1s ease-out;`. Apply the class to `tr` or
  `.card` elements that will be swapped out.
- For out-of-band updates (e.g., counter refresh after mutation), trigger a custom
  DOM event via the `HX-Trigger` header using `htmx_refresh_response()`.
- Do not use `hx-boost` globally — apply htmx attributes selectively and
  explicitly.
- When an htmx response renders a fragment, it must NOT include `<%inherit>` —
  partial templates (e.g., `company_more.mako`) inherit from `layout.mako` only
  when rendered standalone.

## Do's and Don'ts

- **Do** use the `common/button.mako` macros for all action buttons — never write
  raw `<button>` or `<a class="btn ...">` inline in page templates.
- **Do** use `<%include file="..."/>` for reusable fragments; use
  `<%namespace name="..." file="..."/>` + `${ns.macro()}` for parameterized macros.
- **Do** gate mutating UI controls on `request.identity.role` (editor/admin) —
  the `button()` macro handles this automatically.
- **Do** follow the PRG (Post/Redirect/Get) pattern for all form submissions:
  return `HTTPSeeOther` after a successful POST, never render the form response
  directly.
- **Do** prefer `hx-trigger="intersect once"` over `hx-trigger="revealed"` for
  infinite scroll — it fires exactly once per sentinel element.
- **Don't** add custom CSS to `style.css` unless it is strictly necessary and
  cannot be achieved with Bootstrap utilities.
- **Don't** use `<style>` blocks inside Mako templates.
- **Don't** use `onclick="..."` or inline JavaScript; all JS behaviour is either
  htmx-driven or handled by the dedicated `static/js/` scripts.
- **Don't** use Bootstrap's JavaScript API directly (e.g., `new bootstrap.Modal(...)`)
  except in the existing `static/js/` scripts that already do so.
- **Don't** add a second navbar, sidebar, or fixed footer — the layout has a
  single fixed-top navbar and a simple inline footer defined in `base/footer.mako`.
- **Don't** use color for conveying meaning alone (WCAG 1.4.1) — always pair
  color with an icon or text label.
- **Don't** render user-provided content with `| n` unless it has been sanitized
  server-side with `nh3` (as done for markdown comment bodies).
