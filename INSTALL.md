Marker
======

Getting Started
---------------

Change directory into your newly created project if not already there. Your current directory should be the same as this INSTALL.md file and setup.py.

    cd marker

Create a Python virtual environment, if not already created.

    python3 -m venv env

Upgrade packaging tools, if necessary.

    env/bin/pip install --upgrade pip setuptools

Install the wheel package.

    env/bin/pip install --upgrade wheel

Install the project in editable mode with its testing requirements.

    env/bin/pip install -e ".[testing]"

Initialize and upgrade the database using Alembic.

    env/bin/alembic -c development.ini upgrade head

Load default data into the database using a script.

    env/bin/initialize_marker_db development.ini

Run your project's tests.

    env/bin/pytest

Run your project.

    env/bin/pserve development.ini

Log in as admin using default password: admin

Set up an admin account and create user accounts.
