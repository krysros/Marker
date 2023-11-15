# Marker

CRM for General Contractors.

## Usage example

Find the most frequently recommended companies with a specific business profile and projects that meet the required criteria. Check which companies have implemented the largest number of projects, which subdivisions are the most entrepreneurial and in which industries there is the greatest competition.

## Back-end

- Pyramid
- SQLAlchemy

## Front-end

- Bootstrap
- htmx
- Leaflet

## Model diagram

![my_data_model_diagram](my_data_model_diagram.svg)

How to visualize SQLAlchemy Data Models?

1. Install [Graphviz](https://graphviz.org/) and add it to your PATH
2. Install [Roboto](https://fonts.google.com/specimen/Roboto)
3. Install [SQLAlchemy Data Model Visualizer](https://github.com/Dicklesworthstone/sqlalchemy_data_model_visualizer) with `pip install sqlalchemy-data-model-visualizer`
4. Run these commands from Marker venv:

```python
>>> from marker.models import *
>>> from sqlalchemy_data_model_visualizer import generate_data_model_diagram
>>> models = [Activity, Comment, Company, Contact, IdentificationNumber, Project, Tag, Themes, User]
>>> generate_data_model_diagram(models)
```