Internationalization
--------------------

Currently available languages:

- [x] English (en)
- [x] Polish (pl)

Run these commands in project's directory (replace `pl` with your locale):

    python setup.py extract_messages -o marker/locale/messages.pot

    python setup.py init_catalog -l pl -i marker/locale/messages.pot -o marker/locale/pl/LC_MESSAGES/messages.po

    python setup.py update_catalog -l pl -i marker/locale/messages.pot -o marker/locale/pl/LC_MESSAGES/messages.po

    python setup.py compile_catalog -i marker/locale/pl/LC_MESSAGES/messages.po -o marker/locale/pl/LC_MESSAGES/messages.mo
