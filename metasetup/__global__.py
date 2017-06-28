import os 
import sys
from types import ModuleType
from importlib.abc import MetaPathFinder, Loader
from importlib.machinery import ModuleSpec
from importlib.util import module_from_spec


class Bunch(dict):
    """A dict with attribute-access"""

    def __getattr__(self, key):
        try:
            return self.__getitem__(key)
        except KeyError:
            raise AttributeError(key)
    
    def __setattr__(self, key, value):
        self.__setitem__(key, value)
    
    def __dir__(self):
        names = dir({})
        names.extend(self.keys())
        return names

    def __repr__(self):
        return "%s(%r)" % (type(self).__name__, self.copy())


class Settings(Bunch):

    def __new__(cls, name=None, settings=None, parent=None):
        self = super(Settings, cls).__new__(cls)

        if name is not None:

            if parent is None:
                parent = sys.modules[__name__]
                if not isinstance(parent, Settings):
                    raise TypeError("The module %r must be a Settings "
                        "object, not %r" % (__name__, parent))

            names = name.split(".")

            if len(names) > 1:
                shortname = ".".join(names[:-1])
                parent = Settings(shortname, parent=parent)

            if names[-1] in parent:
                self = parent[names[-1]]
            else:
                parent[names[-1]] = self
        
        return self

    def __init__(self, name=None, settings=None, parent=None):
        if name is None:
            fullname = None
        elif not (parent is None or parent.__name__ is None):
            fullname = parent.__name__ + "." + name
        else:
            fullname = name
        object.__setattr__(self, "__name__", fullname)
        super(Settings, self).__init__(settings or {})

    def __getitem__(self, name):
        if name in self:
            return super(Settings, self).__getitem__(name)
        elif name.startswith("_") and name.endswith("_"):
            raise AttributeError("%r" % name)
        else:
            return Settings(name, parent=self)

    def configure(self, obj):
        for k, v in self.items():
            if isinstance(v, Settings):
                v.configure(getattr(obj, k))
            else:
                setattr(obj, k, v)

    def __repr__(self):
        return "%s(%r)" % (type(self).__name__, self.copy())

    def __str__(self):
        return "%s(%r)" % (self.__name__ or type(self).__name__, self.copy())

    @classmethod
    def main(cls):
        if not hasattr(cls, main):
            cls._main = Settings()
        else:
            return cls._main


class SettingsModule(ModuleType):
    """A module whose attributes generate Settings objects when accessed"""

    def __init__(self, spec):
        self.__path__ = None
        self.__file__ = None
        self.__name__ = spec.name
        self.__loader__ = spec.loader
        self.__package__ = ".".join(spec.name.split(".")[:-1])

    def __getattr__(self, name):
        package = self.__name__[len(self.__loader__.basename) + 1:]
        return Settings(package + "." + name)


class SettingsImporter(Loader, MetaPathFinder):

    def __init__(self, basename):
        self.basename = basename

    def find_spec(self, fullname, path, target=None):
        if fullname.startswith(self.basename):
            return ModuleSpec(fullname, self)

    def create_module(self, spec):
        return SettingsModule(spec)

    def exec_module(self, module):
        pass

sys.modules[__name__] = Settings()
sys.meta_path.append(SettingsImporter("metasetup"))
