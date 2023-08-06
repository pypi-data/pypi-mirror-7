ftw.profilehook
===============

ftw.profilehook provides a hook for executing custom code after a
generic setup profile is installed.


Motivation
----------

We often use import steps for executing code after import a generic
setup profile.
Registering a lot of setup handlers is bad because it extends the
import duration of every profile and the amount of import steps are
limited in generic setup, causing bad effects when exceeded.
Import steps are meant to import things from any profile, not for
executing code after importing a specific profile.
Because of these reasons ``ftw.profilehook`` exists and provides an
easy method to solve this issue.



Usage
-----

Add ``ftw.profilehook`` as dependency in your ``setup.py``:

.. code:: python

  setup(...
        install_requires=['ftw.profilehook'])

Register your hook function in ZCML (configure.zcml):

.. code:: xml

  <configure
      xmlns="http://namespaces.zope.org/zope"
      xmlns:genericsetup="http://namespaces.zope.org/genericsetup"
      xmlns:i18n="http://namespaces.zope.org/i18n"
      xmlns:profilehook="http://namespaces.zope.org/profilehook"
      i18n_domain="my.package">

    <include package="ftw.profilehook" />

    <genericsetup:registerProfile
        name="default"
        title="my.package"
        directory="profiles/default"
        provides="Products.GenericSetup.interfaces.EXTENSION"
        />

    <profilehook:hook
        profile="my.package:default"
        handler=".hooks.default_profile_installed"
        />

  </configure>

Do things in your hook (``hooks.py``):

.. code:: python

  from my.package.interfaces import IMyRoot
  from zope.component import alsoProvides


  def default_profile_installed(site):
    mark_site_as_my_root(site)


  def mark_site_as_my_root(site)
    if not IMyRoot.providedBy(site):
      alsoProvides(site, IMyRoot)

After your profile (``my.package:default``) is installed, your hook is executed.



Links
=====

- Github: https://github.com/4teamwork/ftw.profilehook
- Pypi: http://pypi.python.org/pypi/ftw.profilehook
- Tests: https://jenkins.4teamwork.ch/search?q=ftw.profilehook


Copyright
=========

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.profilehook`` is licensed under GNU General Public License, version 2.
