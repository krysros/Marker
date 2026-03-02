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
