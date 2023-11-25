Marker
======

Getting Started
---------------

Change directory into your newly created project if not already there. Your current directory should be the same as this INSTALL.md file and setup.py.

    cd marker

Create and activate a Python virtual environment, if not already created.

    See: https://docs.python.org/3/library/venv.html

Upgrade packaging tools, if necessary.

    pip install --upgrade pip setuptools

Install the project in editable mode with its testing requirements.

    pip install -e ".[testing]"

Initialize and upgrade the database using Alembic.

    alembic -c development.ini upgrade head

Load default data into the database using a script.

    initialize_marker_db development.ini

Run your project's tests.

    pytest

Run your project.

    pserve development.ini


Log in
------

Log in as admin using default password: admin

Set up an admin account and create user accounts.
