2.8
---

- Added stage and role filter dropdowns for projects assigned to a company and companies assigned to a project
- Added reusable dropdown_filter template component with active filter indicator
- Added ODS export support alongside XLSX for companies, projects, contacts, tags and starred/selected views
- Added XLSX/ODS title labels to download buttons across all export views
- Added odfpy dependency for ODS spreadsheet generation with row coloring and column transformers
- Added project fields: usable area, cubic volume, currency, net value and gross value with range-based search and filtering
- Added website uptime check views for companies and projects with Start/Stop control and color-coded HTTP response badges
- Added date-time range filtering (date_from / date_to) for companies, projects, tags, contacts and comments across all list and related views
- Numeric values displayed with two decimal places and narrow non-breaking space as thousands separator
- Standardized locale POT file naming to follow Babel conventions
- Updated Polish translations
- Expanded test coverage to 100%

2.7
---

- Added a keyboard shortcuts modal and expanded global shortcuts for navigation, search, add/edit/delete actions, starring and homepage access
- Added AI-assisted company creation from a website address with Gemini-based autofill, duplicate detection, clearer error handling and loading feedback
- Simplified company and project forms, removed the obsolete company court field and improved related mobile/header layouts
- Improved website autofill and field extraction quality, including better company name and street detection
- Replaced website autofill refresh icons in company and project forms with AI icons and added a growing spinner during autofill requests
- Changed XLSX row coloring to use cell fills only, without colored borders or forced font colors
- Refined exports, search/view behavior and record-name validation across core forms
- AI buttons (company add via AI, website autofill) are now only displayed when the GEMINI_API_KEY environment variable is set
- Updated Polish translations, refreshed dependencies and installation notes, and expanded automated test coverage

2.6
---

- Unified view icons in headers of selected and starred views (e.g. companies, projects, contacts, tags)
- Added "bi bi-tags" icon for the selected tags view
- Added view switchers (e.g. Companies/Contacts, Projects/Contacts, Tag/Companies/Projects/Contacts) in selected and related views for consistent navigation
- Improved Polish translation: "Clear" is now "Wyczyść"
- Updated and compiled Polish translation files

2.5
---

- Added Contractors view with shared filters, company-role filtering and shared search criteria UX
- Added shared-tags sorting, badges and popovers in similar company and project views
- Improved Google Contacts CSV import, guidance and duplicate handling
- Added website autofill/refresh improvements and reorganized website fields in forms
- Enforced contact cascades on company and project deletion
- Improved bulk selection performance, selection-state handling and selected/stars related views
- Added tag category filtering, company/project counters in list views and links from report rows to filtered results
- Expanded contact-tag search filtering/sorting and improved contact list sorting options
- Made text search case-insensitive for Polish characters and fixed Polish alphabetical sorting across text columns
- Hardened auth cookies, markdown sanitization, query counting and ORM helper behavior
- Added admin user deletion modes with optional data purge
- Updated Pyramid/SQLAlchemy-related dependencies and performed layout/theme maintenance cleanups

2.3
---

- Switched project environment/dependency workflow to uv
- Unified and expanded XLSX exports (full fields without `id/created_at/updated_at`, tags at the end, consistent headers in selected/stars/user views)
- Added XLSX export options to user views for companies, projects, tags and contacts
- Added contact filtering and sorting by country, subdivision and color
- Added optional tag-scoped search for companies and projects (including dynamic tag inputs in search forms)
- Improved search criteria UX by including tags in result criteria and preserving them in "Go to the form and add..."
- Improved export robustness by normalizing unsupported values (e.g. `TranslationString`) before writing XLSX

2.2
---

- Reports as a list
- Import from Google Contacts CSV file

2.1
---

- Ability to change locale from the navigation bar

2.0
---

- Display name of company and project of edited activity details as disabled input

2.0rc2
------

- Group templates in folders
- Allow edit activity details

2.0rc1
------

- Update migrations (remove `themes` table from database)
- Improve themes
- Validation errors below form fields instead of flash messages

2.0b6
-----

- Improve export (subdivision and country columns)
- Remove flash message after 3s
- Reset migrations
- Moved identification numbers to company

2.0b5
-----

- Add/edit an identification numbers

2.0b4
-----

- Replace overcomplicated modals with simple forms

2.0b3
-----

- More filters and maps
- Bug fixes

2.0b2
-----

- Add maps to user's views of companies and projects
- Add filters

2.0b1
-----

- Added maps in user profile
