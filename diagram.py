"""
Generates a diagram of all SQLAlchemy models in marker.models.
See DIAGRAM.md for requirements and usage.
"""

import inspect
from typing import List, Type

from sqlalchemy_data_model_visualizer import generate_data_model_diagram

import marker.models


def get_models() -> List[Type]:
    """Collect all SQLAlchemy models from marker.models."""
    models = []
    for name, obj in inspect.getmembers(marker.models):
        if inspect.isclass(obj) and hasattr(obj, "__tablename__"):
            models.append(obj)
    return models


if __name__ == "__main__":
    models = get_models()
    if not models:
        print("No models found in marker.models.")
    else:
        try:
            generate_data_model_diagram(models, output_file="my_data_model_diagram")
            print("Diagram generated: my_data_model_diagram.svg")
        except Exception as e:
            print(f"Error generating diagram: {e}")
