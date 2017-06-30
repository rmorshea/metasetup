from ._metasetup import (import_global_settings, import_local_settings,
    global_settings, local_settings, Settings, GlobalSettings)

class Configurable(object):

    @classmethod
    def settings_mro(cls):
        for c in cls.mro():
            yield (c, local_settings(c.__module__, c.__name__))

    @classmethod
    def settings(cls):
        mine = Settings()
        for c, s in cls.settings_mro():
            mine.merge(s)
        return mine

    def configure(self):
        settings = self.settings()
        settings.configure(self)
        return settings
