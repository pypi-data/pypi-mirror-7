configless
========================================

configless is tiny small configurator, inspired by pyramid's configurator.
but this is silly not comprehensive.

how to use
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

you can develop foo function, so IHasFoo interface.
and you are providing two variants of foo function.
(my.foo and your.foo are these)

.. code:: python

    ## definition
    from zope.interface import Interface, implementer
    from configless.interfaces import IPlugin

    class IHasFoo(Interface):
        def foo():
            pass

    @implementer(IHasFoo, IPlugin)
    class MyFoo(object):
        @classmethod
        def create_from_setting(cls, settings):
            return cls()

        def foo(self):
            return "my"

    @implementer(IHasFoo)
    class YourFoo(object):
        @classmethod
        def create_from_setting(cls, settings):
            return cls()

        def foo(self):
            return "your"


    ## using
    from configless import Configurator
    config = Configrator()

    ## install many plugins about `foo`
    config.add_plugin("my.foo", MyFoo, categoryname="foo")
    config.add_plugin("your.foo", YourFoo, categoryname="foo")

    ## activate my.foo plugin, then, my.foo is used by plugin about `foo`.
    result = config.activate_plugin("my.foo")

    ## so, configurator has function about result
    config.foo.foo() # => "my"

summary
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

you can provides 'foo' function

- define plugin
- install plugin -- via config.add_plugin(..)
- activate plugin -- via config.activate_plugin(..)
