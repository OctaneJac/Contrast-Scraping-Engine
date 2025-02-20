import importlib
import pkgutil
import scrapy
from scraper_archive.scraper_archive.spiders import __name__ as spiders_module

def get_all_spiders():
    """
    Scans the spiders directory and returns a dictionary mapping spider names to their classes.
    """
    spider_classes = {}
    package = importlib.import_module(spiders_module)

    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        module = importlib.import_module(f"{spiders_module}.{module_name}")

        # Find classes that inherit from scrapy.Spider
        for attr in dir(module):
            obj = getattr(module, attr)
            if isinstance(obj, type) and issubclass(obj, scrapy.Spider) and obj is not scrapy.Spider:
                spider_classes[obj.name] = obj  # Map spider name to the class

    return spider_classes

print(get_all_spiders())