# catalog_utils.py
from main.models import Catalog

def get_available_catalog_count():
    """
    Returns a dictionary mapping catalog id to available count.
    """
    result = {}
    for catalog in Catalog.objects.all():
        result[str(catalog.id)] = catalog.available_count()
    return result
