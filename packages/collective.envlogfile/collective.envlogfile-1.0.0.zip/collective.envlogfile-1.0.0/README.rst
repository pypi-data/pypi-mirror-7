Envlogfile
==========

Provides ZConfig_-compatible logfile handler called ``envlogfile``, which
is otherwise similar to the default ``logfile`` handler, but interpolates
environment variables in the given log file path name.

.. code:: python

   path = self.section.path % os.environ

Usage with `plone.recipe.zope2instance`_:

.. _ZConfig: https://pypi.python.org/pypi/ZConfig
.. _plone.recipe.zope2instance: https://pypi.python.org/pypi/plone.app.zope2instance

.. code:: ini

   [instance]
   event-log-custom =
       %import collective.envlogfile
       <envlogfile>
           path %(MY_ENV_FOLDER)s/instance.log
           level INFO
       </envlogfile>
