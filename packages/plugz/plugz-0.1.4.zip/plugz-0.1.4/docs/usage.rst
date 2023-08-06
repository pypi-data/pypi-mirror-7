========
Usage
========

plugz will let you define custom types of plugins. You will then derive from your new type to create plugin classes and provide plugz with the location of these new plugins. plugz can then provide you with a loading mechanism for these plugin classes.

The main idea is to derive your custom plugin type from plugz.PluginTypeBase and
declare all the methods that plugins will need to implement as abstract. Look at how a type that plugz ships with is implemented:

.. literalinclude:: /../plugz/plugintypes/standard_plugin_type.py

Just include the implementation of your custom type in your application and pass it on to plugz when necessary. How to do that is described later when we show the load_plugins() function.

The according plugins can look like the following. Note the usage of plugz.register_plugin.

.. literalinclude:: /../tests/data/plugins/standard/valid/plugin_one.py

Given that you defined a plugin type like described above, as well as plugins that derive correctly from it, the following simple instructions will return a list of all registered, valid plugin classes:

>>> import plugz
>>> import my_host_app.MyNewPluginType
>>> plugins = plugz.load_plugins(['/path/to/my/plugins/'], my_host_app.MyNewPluginType)

.. note:: plugz will return a list of class objects and not a list of instances of these objects! You will need to initialize your plugins yourself if you need an actual instance.
