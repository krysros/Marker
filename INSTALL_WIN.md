Marker
======

Getting Started
---------------

Change directory into your newly created project if not already there. Your current directory should be the same as this INSTALL.md file and setup.py.

    cd marker

Create a Python virtual environment, if not already created.

    python -m venv env

Upgrade packaging tools, if necessary.

    .\env\Scripts\pip.exe install --upgrade pip setuptools

Install the wheel package.

    .\env\Scripts\pip.exe install --upgrade wheel

Install the project in editable mode with its testing requirements.

    .\env\Scripts\pip.exe install -e ".[testing]"

Initialize and upgrade the database using Alembic.

    .\env\Scripts\alembic.exe -c development.ini upgrade head

Load default data into the database using a script.

    .\env\Scripts\initialize_marker_db.exe development.ini

Run your project's tests.

    .\env\Scripts\pytest.exe

Run your project.

    .\env\Scripts\pserve.exe development.ini

Log in as admin using default password: admin

Set up an admin account and create user accounts.
