=========
MetaSetup
=========

A package for configuring settings and initializing objects.

-------
Summary
-------

With ``metasetup``, there are no configuration files, just python modules which import
and modify settings. This means, that these modules can be used as a "meta" layer on top
of normal configuration files, or to programatically configure the settings themselves.
To access the settings for a particular module, one need only import it with ``metasetup``
as a prefix (e.g. ``from metasetup.my_package import my_module``) and use its attributes.

------------------------
Installation and Testing
------------------------

Install ``metasetup`` using ``pip``:

.. code-block:: text
    
    pip install metasetup

Run the tests with ``pytest``:

.. code-block:: text
    
    py.test metasetup

For a developer's installation:

1. clone this github repository
2. ``cd`` into the parent directory
3. run ``$ pip install -e .``

-----------
Basic Usage
-----------

For demonstration purposes, we can create a contrived scenario in which the python module
configuring settings and the one being configured are the same. Consider the python file
which is run by ``python main.py`` and has the following contents:

.. code-block:: python

    # Import the settings we wish to configure

    from metasetup.__main__ import MyClass as MyClassSettings

    # and modify the settings as we please

    MyClassSettings.x = 1
    print(MyClassSettings)

    # We then define the Configurable class we want to initialize

    from metasetup import Configurable

    class MyClass(Configurable):
        """The class whose instances we are about to configure"""
        pass

    # Finally, we can create an instance of our class and configure it

    mc = MyClass()
    mc.configure()
    print(mc.x)

    # Vualá! The instances of our class can be configured.

--------------
Under The Hood
--------------

In order to import settings, a ``SettingsImporter`` is appended to Python's `meta path`_. Every time a name not
defined in ``metasetup/__init__.py`` is requested, the importer creates a ``SettingsModule``. The attributes of
these modules contain ``Settings`` which can be modified, and used to initialize ``Configurable`` instances. All
``Settings`` are stored globally, and accessible via ``metapath.import_settings()``.

.. _meta path: https://docs.python.org/library/sys.html#sys.meta_path
