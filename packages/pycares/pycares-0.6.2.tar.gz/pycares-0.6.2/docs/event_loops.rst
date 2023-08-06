.. _event_loops:

======================
Event loop integration
======================


pycares can be integrated in an already existing event loop without much trouble.
The examples folder contains several examples:

* cares-select.py: ntegration with plain select
* cares-resolver.py: integration with the pyuv event loop
* cares-asyncio.py: integration with the asyncio framework

Additionally, `Tornado <http://tornadoweb.org>`_ provides integration
with pycaes through a `resolver module <https://github.com/facebook/tornado/blob/master/tornado/platform/caresresolver.py>`_.

