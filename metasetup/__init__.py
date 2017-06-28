import sys
from . import __global__


def import_settings(name=None, from_name=None):
    module = sys.modules["importlib"].import_module("metasetup." + (name or "__global__"))
    if from_name is not None:
        return getattr(module, from_name)
    else:
        return module


class Configurable(object):

    @classmethod
    def import_my_settings(cls):
        return import_settings(cls.__module__, cls.__name__)

    def configure(self):
        my_settings = self.import_my_settings()
        my_settings.configure(self)
        return my_settings
