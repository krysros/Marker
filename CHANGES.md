2.0a6
-----

- **BREAKING CHANGE**: Add new tables: `projects_tags`, `projects_persons`, `projects_comments`

2.0a5
-----

- **BREAKING CHANGE**: Rename recomend table to recommend
- **BREAKING CHANGE**: Rename WWW column to link in company
- Add color column to project

2.0a4
-----

- Update psycopg (a.k.a. psycopg 3)

2.0a3
-----

- Add country do company and project
- Update counters via events
- Extend and improve UI

2.0a2
-----

- Add maps to views
- Add slug to person

2.0a1
-----

- **BREAKING CHANGE**: Drop *documents* table
- **BREAKING CHANGE**: Drop *phone* and *email* from *companies* table
- **BREAKING CHANGE**: Renamed many tables and columns
- **BREAKING CHANGE**: Replace bcrypt with argon2
- Replace deform by WTForms
- Upgrade Bootstrap
- Remove jQuery as dependency
- Use htmx to issue AJAX requests directly from HTML
