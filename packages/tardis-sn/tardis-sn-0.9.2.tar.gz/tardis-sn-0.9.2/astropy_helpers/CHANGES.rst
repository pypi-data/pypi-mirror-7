0.4 (unreleased)
----------------

- Initial release of astropy-helpers.  See `APE4
  <https://github.com/astropy/astropy-APEs/blob/master/APE4.rst>`_ for
  details of the motivation and design of this package.

- The ``astropy_helpers`` package replaces the following modules in the
  ``astropy`` package:

  - ``astropy.setup_helpers`` -> ``astropy_helpers.setup_helpers``

  - ``astropy.version_helpers`` -> ``astropy_helpers.version_helpers``

  - ``astropy.sphinx`` - > ``astropy_helpers.sphinx``

  These modules should be considered deprecated in ``astropy``, and any new,
  non-critical changes to those modules will be made in ``astropy_helpers``
  instead.  Affiliated packages wishing to make use those modules (as in the
  Astropy package-template) should use the versions from ``astropy_helpers``
  instead, and include the ``ah_bootstrap.py`` script in their project, for
  bootstrapping the ``astropy_helpers`` package in their setup.py script.
