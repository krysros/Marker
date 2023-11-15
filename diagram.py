import inspect
import marker.models
from sqlalchemy_data_model_visualizer import generate_data_model_diagram

models = []

for name, obj in inspect.getmembers(marker.models):
    if inspect.isclass(obj) and hasattr(obj, "__tablename__"):
        models.append(obj)

generate_data_model_diagram(models)
