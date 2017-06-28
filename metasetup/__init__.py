from .__global__ import import_global_settings, import_local_settings, Settings, GlobalSettings


class MetaConfigurable(type):

    def __init__(cls, name, bases, classdict):
        cls.my_settings = import_local_settings(cls.__module__, cls.__name__)


class Configurable(object, metaclass=MetaConfigurable):

    @classmethod
    def sync_settings(cls):
        for c in cls.mro():
            if issubclass(c, Configurable):
                c.my_settings = import_local_settings(c.__module__, c.__name__)

    @classmethod
    def settings(cls):
        mine = Settings()
        for c in reversed(cls.mro()):
            if issubclass(c, Configurable):
                mine.merge(c.my_settings)
        return mine

    def configure(self):
        settings = self.settings()
        settings.configure(self)
        return settings
