Marker
======

Getting Started
---------------

Change directory into your newly created project if not already there. Your current directory should be the same as this INSTALL.md file and pyproject.toml.

    cd marker

Install the project with its testing requirements.

    uv sync --extra testing

Initialize and upgrade the database using Alembic.

    uv run alembic -c development.ini upgrade head

Load default data into the database using a script.

    uv run initialize_marker_db development.ini

Run your project's tests.

    uv run pytest

Run your project.

    uv run pserve development.ini --reload



Log in
------

Log in as "admin" using default password: admin

Set up an admin account and create user accounts.
