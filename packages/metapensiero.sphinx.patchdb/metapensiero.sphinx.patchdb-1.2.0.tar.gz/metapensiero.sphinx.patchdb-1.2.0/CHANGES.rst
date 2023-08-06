Changes
-------

1.2.0 (2014-06-19)
~~~~~~~~~~~~~~~~~~

* New "run-always" scripts

* Poor man "CREATE DOMAIN" for MySQL

* User defined assertions


1.1.2 (2014-06-05)
~~~~~~~~~~~~~~~~~~

* New --assume-already-applied option, useful when you start using ``patchdb``
  on an already existing database


1.1.1 (2014-06-03)
~~~~~~~~~~~~~~~~~~

* Fix packaging, adding a MANIFEST.in


1.1.0 (2014-06-03)
~~~~~~~~~~~~~~~~~~

* Use setuptools instead of distribute

* Use argparse instead of optparse

* New mimetype property on scripts, to select the right Pygments highlighter

* New MySQL specific context, using cymysql


1.0.7 (2013-08-23)
~~~~~~~~~~~~~~~~~~

* published on bitbucket


1.0.6 (2013-03-12)
~~~~~~~~~~~~~~~~~~

* dbloady: ability to load field values from external files


1.0.5 (2013-03-11)
~~~~~~~~~~~~~~~~~~

* dbloady: fix encoding error when printing messages coming from PostgresQL

* dbloady: emit a progress bar on stderr


1.0.4 (2013-02-27)
~~~~~~~~~~~~~~~~~~

* dbloady, a new utility script, to load base data from a YAML stream.


1.0.3 (2012-11-07)
~~~~~~~~~~~~~~~~~~

* Fix ``:patchdb:script`` role


1.0.2 (2012-10-19)
~~~~~~~~~~~~~~~~~~

* Pickier way to split the multi-statements SQL scripts, now the
  ``;;`` separator must be on a line by its own

* More precise line number tracking when applying multi-statements SQL
  scripts

* Dump and load script dependencies and conditions as lists, to avoid
  pointless repeated splits and joins


1.0.1 (2012-10-13)
~~~~~~~~~~~~~~~~~~

* Fix error loading JSON storage, simplejson already yields unicode strings

* Possibly use the original title of the script as description, if not
  explicitly set

* More precise error on unknown script reference

* Minor corrections


1.0 (2012-10-10)
~~~~~~~~~~~~~~~~

* Added JSON support for the on disk `scripts storage`

* Adapted to work with SQLAlchemy 0.7.x

* Updated to work with docutils > 0.8

* Refactored as a `Sphinx domain <http://sphinx.pocoo.org/domains.html>`_

  .. attention:: This means that the directive names are now prefixed
                 with ``patchdb:`` (that is, the old ``script``
                 directive is now ``patchdb:script``). You can use the
                 `default-domain`__ directive if that annoys you.

  __ http://sphinx.pocoo.org/domains.html#directive-default-domain

* Renamed the status table from ``prst_applied_info`` to simply
  ``patchdb``

  .. attention:: This is the main incompatible change with previous
                 version: you should eventually rename the table
                 manually, sorry for the inconvenience.

* Renamed ``prst_patch_storage`` configuration setting to
  ``patchdb_storage``

* Each script ID is now lower case, to avoid ambiguities


0.3 (2010-11-14)
~~~~~~~~~~~~~~~~

* Updated to work with Sphinx 1.0

* New :script: role for cross-references

* New :file: option on script directive, to keep the actual text in an
  external file


0.2 (2010-03-03)
~~~~~~~~~~~~~~~~

* Compatibility with SQLAlchemy 0.6

* New patchdb command line tool


0.1 (2009-10-28)
~~~~~~~~~~~~~~~~

* Replace home brew solution with SQLAlchemy topological sort

* Use YAML for the persistent storage

* Mostly working Sphinx adaptor

* Rudimentary and mostly untested SQLAlchemy backend (basically only
  the direct PostgresQL backend has been battle tested in production...)

* First standalone version


0.0
~~~

* still a PylGAM side-product

* simply a set of docutils directives

* started with Firebird in mind, but grown up with PostgresQL
