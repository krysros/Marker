Internationalization
--------------------

Currently available languages:

- [x] English (en)
- [x] Polish (pl)

Run these commands in project's directory (replace `pl` with your locale):

    pybabel extract -F babel.cfg -o marker/locale/marker.pot .

    pybabel init -i marker/locale/marker.pot -d marker/locale -l pl

    pybabel update -i marker/locale/marker.pot -d marker/locale

    pybabel compile -d marker/locale
