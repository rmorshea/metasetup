import os
import ast
import sys
import argparse
from types import ModuleType
from importlib import import_module
from importlib.abc import MetaPathFinder, Loader
from importlib.machinery import ModuleSpec
from importlib.util import module_from_spec


class _Undefined(object):
    pass


Undefined = _Undefined()


class Bunch(dict):
    """A dict with from_name-access"""

    def __getattr__(self, key):
        try:
            return self.__getitem__(key)
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __delattr__(self, key):
        self.__delitem__(key)

    def __dir__(self):
        names = dir({})
        names.extend(self.keys())
        return names

    def __repr__(self):
        return "%s(%s)" % (type(self).__name__, repr(dict(self))[1:-1])


class GlobalSettings(Bunch):

    def __new__(cls, name=None, settings=None, parent=None):
        self = super(GlobalSettings, cls).__new__(cls)

        if name is not None:

            parent = parent or GLOBAL
            names = name.split(".")

            if len(names) > 1:
                shortname = ".".join(names[:-1])
                parent = GlobalSettings(shortname, parent=parent)

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
        super(GlobalSettings, self).__init__(settings or {})

    def __getitem__(self, name):
        if name in self:
            return super(GlobalSettings, self).__getitem__(name)
        elif name.startswith("_") and name.endswith("_"):
            raise KeyError("%r" % name)
        else:
            return GlobalSettings(name, parent=self)

    def localize(self):
        return Settings({k : (v.localize()
            if isinstance(v, GlobalSettings) else v)
            for k, v in self.items()})


class GlobalSettingsModule(ModuleType):
    """A module whose from_names generate Settings objects when accessed"""

    def __init__(self, spec):
        self.__path__ = None
        self.__file__ = None
        self.__name__ = spec.name
        self.__loader__ = spec.loader
        self.__package__ = ".".join(spec.name.split(".")[:-1])
        self._settings = GlobalSettings(self.__name__[len(self.__loader__.basename) + 1:])

    def __getattr__(self, name):
        package = self.__name__[len(self.__loader__.basename) + 1:]
        settings = GlobalSettings(package + "." + name)
        setattr(self, name, settings)
        return settings


class GlobalSettingsImporter(Loader, MetaPathFinder):

    basename = "metasetup"

    def find_spec(self, fullname, path, target=None):
        if fullname.startswith(self.basename):
            return ModuleSpec(fullname, self)

    def create_module(self, spec):
        return GlobalSettingsModule(spec)

    def exec_module(self, module):
        pass


GLOBAL = GlobalSettings()
sys.meta_path.append(GlobalSettingsImporter())


def to_fullname(name, package=None):
    if package is not None:
        return ".".join((GlobalSettingsImporter.basename, package, name))
    else:
        return ".".join((GlobalSettingsImporter.basename, name))


def import_global_settings(name=None, from_name=None, package=None):
    if name is None:
        module = GLOBAL
    else:
        module = import_module(to_fullname(name, package))
    if from_name is not None:
        return getattr(module, from_name)
    else:
        return module


def import_local_settings(name=None, from_name=None):
    return import_global_settings(name, from_name).localize()


def global_settings(*names):
    settings = GLOBAL
    for name in ".".join(names).split("."):
        try:
            settings = settings[name]
        except KeyError:
            return None
    return settings


def local_settings(*names):
    settings = global_settings(*names)
    return settings.localize() if settings else Settings()


class Settings(Bunch):

    def __contains__(self, name):
        if "." not in name:
            return super(Settings, self).__contains__(name)
        else:
            first = name[:name.index(".")]
            return (super(Settings, self).__contains__(first) and
                isinstance(self[first], Settings) and
                name[len(first) + 1:] in self[first])

    def __getitem__(self, name):
        if "." not in name:
            return super(Settings, self).__getitem__(name)
        else:
            settings = self
            names = name.split(".")
            for i in range(len(names)):
                settings = settings[names[i]]
                if not isinstance(settings, Settings):
                    raise KeyError(".".join(names[:i + 1]))
            return settings

    def __setitem__(self, name, value):
        if "." not in name:
            super(Settings, self).__setitem__(name, value)
        else:
            name, ending = name.rsplit(".", 1)
            self.get(name)[ending] = value

    def __delitem__(self, name):
        if "." not in name:
            super(Settings, self).__delitem__(name)
        else:
            name, ending = name.rsplit(".", 1)
            del self[name][ending]

    def get(self, name, default=Undefined):
        if "." not in name:
            if name in self:
                return self[name]
            elif default is Undefined:
                settings = Settings()
                self[name] = settings
                return settings
            else:
                return default
        else:
            settings = self
            names = name.split(".")
            for n in names:
                settings = settings.get(n)
            return settings


    def configure(self, obj, keys=None):
        for k in (keys or self):
            v = self[k]
            if isinstance(v, Settings):
                v.configure(getattr(obj, k))
            else:
                setattr(obj, k, v)

    def merge(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            if isinstance(v, Settings) and isinstance(self.get(k), Settings):
                self[k].merge(v)
            else:
                self[k] = v

    @classmethod
    def from_dictionary(cls, mapping):
        new = cls()
        for k in mapping:
            _new = new
            v = mapping[k]
            if "." in k:
                for subk in k.split("."):
                    _new = _new.setdefault(subk, {})
            if isinstance(v, dict):
                v = cls.from_mapping(v)
            _new[k] = v
        return new

    def __repr__(self):
        return repr(dict(self))


class ArgumentParser(argparse.ArgumentParser):

    def __init__(self, *args, **kwargs):
        super(ArgumentParser, self).__init__(*args, **kwargs)
        self._settings = []

    def add_settings(self, name, from_name=None, package=None, *args, **kwargs):
        fullname = name
        if package is not None:
            fullname = "%s.%s" % (package, fullname)
        if from_name is not None:
            fullname = "%s.%s" % (fullname, from_name)
        self.add_argument("--" + fullname, dest="_" + fullname.replace(".", "_"),
            help="settings for %r" % fullname, *args, **kwargs, nargs="+")
        self._settings.append(fullname)

    def parse_settings(self, *args, **kwargs):
        settings = Settings()
        ns = super(ArgumentParser, self).parse_args(*args, **kwargs)
        for name in self._settings:
            args = getattr(ns, "_" + name.replace(".", "_"))
            for arg in args:
                k, v = arg.split("=")
                settings[k] = ast.literal_eval(v)
        return settings
