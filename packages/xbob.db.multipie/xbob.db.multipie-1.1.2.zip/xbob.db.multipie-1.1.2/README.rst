====================
 Multi-PIE Database
====================

This package contains the access API and descriptions for the `Multi-PIE
Database <http://www.multipie.org/>`_. The actual raw data for
the database should be downloaded from the original URL. This package only
contains the `Bob <http://www.idiap.ch/software/bob/>`_ accessor methods to use
the DB directly from python, with our certified protocols.

You would normally not install this package unless you are maintaining it. What
you would do instead is to tie it in at the package you need to **use** it.
There are a few ways to achieve this:

1. You can add this package as a requirement at the ``setup.py`` for your own
   `satellite package
   <https://github.com/idiap/bob/wiki/Virtual-Work-Environments-with-Buildout>`_
   or to your Buildout ``.cfg`` file, if you prefer it that way. With this
   method, this package gets automatically downloaded and installed on your
   working environment, or

2. You can manually download and install this package using commands like
   ``easy_install`` or ``pip``.

The package is available in two different distribution formats:

1. You can download it from `PyPI <http://pypi.python.org/pypi>`_, or

2. You can download it in its source form from `its git repository
   <https://github.com/bioidiap/xbob.db.multipie>`_. When you download the
   version at the git repository, you will need to run a command to recreate
   the backend SQLite file required for its operation. This means that the
   database raw files must be installed somewhere in this case. With option
   ``a`` you can run in `dummy` mode and only download the raw data files for
   the database once you are happy with your setup.

You can mix and match points 1/2 and a/b above based on your requirements. Here
are some examples:

Modify your setup.py and download from PyPI
===========================================

That is the easiest. Edit your ``setup.py`` in your satellite package and add
the following entry in the ``install_requires`` section (note: ``...`` means
`whatever extra stuff you may have in-between`, don't put that on your
script)::

    install_requires=[
      ...
      "xbob.db.multipie",
    ],

Proceed normally with your ``boostrap/buildout`` steps and you should be all
set. That means you can now import the ``xbob.db.multipie`` namespace into your scripts.

Modify your buildout.cfg and download from git
==============================================

You will need to add a dependence to `mr.developer
<http://pypi.python.org/pypi/mr.developer/>`_ to be able to install from our
git repositories. Your ``buildout.cfg`` file should contain the following
lines::

  [buildout]
  ...
  extensions = mr.developer
  auto-checkout = *
  eggs = bob
         ...
         xbob.db.multipie

  [sources]
  xbob.db.multipie = git https://github.com/bioidiap/xbob.db.multipie.git
  ...

=================
 Using protocols
=================

For simplicity, by default all provided protocols are enabled. This makes the
database query a bit slow. If you don't want to wait each time you query the
database, you can re-create the database on your own. For that, you have to
follow the "download from git" recipe. After doing the bootstrap/buildout step
(see `here
<http://www.idiap.ch/software/bob/docs/releases/last/sphinx/html/OrganizeYourCode.html>`_
for details) in your main directory, you have to go to the (newly created)
directory ``src/xbob.db.multipie`` and do the same bootstrap/buildout step
again. Finally, you can use the `Bob <http://www.idiap.ch/software/bob/>`_ API:
``bin/bob_dbmanage.py multipie create --help`` to regenerate the SQLite file
based on your criteria.

Afterward, only the requested protocols should be available. If not, please
`file a bug <https://github.com/bioidiap/xbob.db.multipie/issues>`_ to get help.


=================================
 Note to the package maintainers
=================================

On PyPI, we used to provide the database with all the protocols enabled.
This means that the database has to be generated as follows, before the packaging:
``bin/bob_dbmanage.py multipie create -P -E``.
