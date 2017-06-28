A package for configuring settings and initializing objects.

With ``metasetup``, there are no configuration files, just python modules which import
and modify settings. This means, that these modules can be used as a "meta" layer on top
of normal configuration files, or to programatically configure the settings themselves.
To access settings for a particular module, one need only import it with ``metasetup``
as a prefix (e.g. ``from metasetup.my_package import my_module``) and use its attributes.

See GitHub_ for more info

.. _GitHub: https://github.com/rmorshea/metasetup
