Changelog
=========

4.0 - August 29, 2014
---------------------

- Remove all SQLAlchemy-pyramid integration logic in favour of using
  `pyramid_sqlalchemy <https://pypi.python.org/pypi/pyramid_sqlalchemy>`_.

3.5 - February 27, 2014
-----------------------

- Add a JSON column type which uses database-native json types where
  possible (ie JSON for PostgreSQL).


3.4 - January 20, 2014
----------------------

- Add an Array column type which uses database-native array types where
  possible (ie ARRAY for PostgreSQL).


3.3 - December 19, 2013
-----------------------

- Add support for Python 3.3 and later.

- Modify UUID type to always use the native string type of the current Python
  version for its values.


3.2 - November 26, 2013
-----------------------

- Make Session object easier to use: instead of creating it on initialisation
  create it immediately, and only configure it during initialisation. This
  makes it possible to import the Session directly.


3.1.2 - May 6, 2013
-------------------

- Modify GUID type to always use a bytestring for uuids. This works around
  problems with SQLAlchemy's identity map when new UUID instances are created
  for the same uuid value.


3.1.1 - May 6, 2013
-------------------

- Make sure event-handlers are registered on every package use.

- Remove stray debug print.

3.1 - May 6, 2013
-----------------

- Add a magic s4u.sqlalchemy.model module with all instrumented classes.

- Remove s4u.upgrade support; we are migrating to alembic and are phasing
  s4u.upgrade support out.

3.0 - May 6, 2013
-----------------

- Add a Mapping column type which uses database-native mapping types where
  possible (ie HSTORE for PostgreSQL).


2.7 - April 18, 2013
--------------------

- Update DatabaseTestCase to call setUp and tearDown of its super classes.


2.6 - January 8, 2013
-----------------------

- First public release.


2.5 - December 10, 2012
-----------------------

- Modify upgrade content provider to always mark the transaction as changed so
  DDL is flushed in a commit. Again - this change got lost somewhere.


2.4 - December 10, 2012
-----------------------

- Do not create multiple engines when our upgrade context provider is used
  multiple times.


2.3 - February 28, 2012
-----------------------

- Modify upgrade content provider to always mark the transaction as
  changed so DDL is flushed in a commit.
  [wichert]

- Make database URL used in DatabaseTestCase configurable via a new
  ``db_uri`` class variable.
  [wichert]

- Abort transaction earlier during test breakdown so we do not try to
  drop tables while another connection is open within a transaction.
  [wichert]


2.2 - January 31, 2012
----------------------

- Update alembic 0.2.0 release which changed its API especially for us.
  [wichert]


2.1 - January 4, 2011
---------------------

- Update DatabaseTestCase to abort any open transaction. This clears out all
  open SQL connections.
  [wichert]


2.0 - January 3, 2011
---------------------

- Setup an `alembic <http://pypi.python.org/pypi/alembic>`_ context
  as part of the upgrade context.
  [wichert]


1.8 - December 28, 2011
-----------------------

- Make creation of database tables optional in DatabaseTestCase.


1.7 - December 28, 2011
-----------------------

- Remove bad docstring from DatabaseTestCase class.

- Expose SQLAlchemy engine in test class as `engine` attribute,
  and fully dispose of the engine on test teardown.


1.6 - November 9, 2011
----------------------

- Move dummy test class inside of test class so it does not pollute
  metadata of real applications.

- Add an INET type to handle IPv4 and IPv6 networks and addresses.
  On the Python side these are handled as IPy.IP instances.


1.5 - September 19, 2011
------------------------

- Add :py:func:`day_difference <s4u.sqlalchemy.func.day_difference>`
  SQL function.


1.4 - September 14, 2011
------------------------

- Include (very minimal) GUID documentation.

- Add :py:func:`least <s4u.sqlalchemy.func.least>` and
  :py:func:`least <s4u.sqlalchemy.func.greatest>` SQL functions.


1.3 - August 31, 2011
---------------------

- Add basic s4u.upgrade integration.


1.2 - August 4, 2011
--------------------

- Fix Pyramid ``includeme`` support.


1.1 - August 4, 2011
--------------------

- Loosen SQLAlchemy dependency to > 0.6.

- Add a uuid column type.


1.0 - August 2, 2011
--------------------

- First version.
