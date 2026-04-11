Internationalization
--------------------

Currently available languages:

- [x] English (en)
- [x] Polish (pl)

Run these commands in project's directory (replace `pl` with your locale):

    uv run pybabel extract -F babel.cfg -o marker/locale/messages.pot .

    uv run pybabel init -i marker/locale/messages.pot -d marker/locale -l pl

    uv run pybabel update -i marker/locale/messages.pot -d marker/locale

    uv run pybabel compile -d marker/locale

