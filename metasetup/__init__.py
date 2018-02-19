from ._metasetup import global_settings, local_settings, Settings, ArgumentParser


class Configurable(object):

    @classmethod
    def settings(cls, **kwargs):
        if kwargs.get("sync", False):
            cls.sync_settings()
        mine = Settings()
        for c in reversed(cls.mro()):
            if issubclass(c, Configurable):
                settings = local_settings(c.__module__, c.__name__)
                mine.merge(settings)
        return mine

    def configure(self, **kwargs):
        keys = kwargs.pop("keys", None)
        settings = self.settings(**kwargs)
        settings.configure(self, keys)
        return settings
