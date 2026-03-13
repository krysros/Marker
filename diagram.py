"""
Generates a diagram of all SQLAlchemy models in marker.models.
See DIAGRAM.md for requirements and usage.
"""

import importlib
import inspect
from collections.abc import Callable

import marker.models


def get_models() -> list[type[object]]:
    """Collect all SQLAlchemy models from marker.models."""
    models: list[type[object]] = []
    for name, obj in inspect.getmembers(marker.models):
        if inspect.isclass(obj) and hasattr(obj, "__tablename__"):
            models.append(obj)
    return models


def _load_diagram_generator() -> Callable[..., object] | None:
    try:
        module = importlib.import_module("sqlalchemy_data_model_visualizer")
    except ImportError:
        return None

    generator = getattr(module, "generate_data_model_diagram", None)
    if callable(generator):
        return generator
    return None


if __name__ == "__main__":
    models = get_models()
    if not models:
        print("No models found in marker.models.")
    generator = _load_diagram_generator()
    if generator is None:
        print("Missing dependency: install sqlalchemy-data-model-visualizer.")
    else:
        try:
            generator(models, output_file="my_data_model_diagram")
            print("Diagram generated: my_data_model_diagram.svg")
        except Exception as e:
            print(f"Error generating diagram: {e}")
