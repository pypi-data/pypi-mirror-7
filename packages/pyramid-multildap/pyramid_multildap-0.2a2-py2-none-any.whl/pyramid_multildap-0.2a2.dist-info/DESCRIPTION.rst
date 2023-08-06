``pyramid_multildap``
=====================

``pyramid_multildap`` is a friendly fork of `pyramid_ldap`_,
incorporating some changes which have been proposed upstream,
but have not been accepted (yet?).

The package is being developed at github:

https://github.com/lmctv/pyramid_multildap

.. include:: ORIG_README.rst

.. _`pyramid_ldap`: https://github.com/Pylons/pyramid_ldap


Original README follows:

``pyramid_ldap``
================

``pyramid_ldap`` provides LDAP authentication services for your Pyramid
application.  Thanks to the ever-awesome `SurveyMonkey
<http://surveymonkey.com>`_ for sponsoring the development of this package!

See the documentation at
http://docs.pylonsproject.org/projects/pyramid_ldap/en/latest/ for more
information.

This package will only work with Pyramid 1.3a9 and better.


Changes:
Next release
------------

- Add attrlist to LDAPQuery, set_login_query, set_groups_query to allow
  retrieved attributes to be filtered. (Default: All attributes on users, no
  attributes on groups). See https://github.com/Pylons/pyramid_ldap/pull/8

- Support creation of multiple co-existing ldap contexts in the same
  application. See https://github.com/Pylons/pyramid_ldap/pull/6

- Add a "search_after_bind" attribute to the _LDAPQuery class, to
  help in reading directory entry attributes when the directory server
  is configured to hide them in the before login search phase.
  See https://github.com/Pylons/pyramid_ldap/pull/5

- Set a size limit on pre-login entry dn searches.

- Escape user-provided login names, avoiding server errors or trivial
  DOSs caused by user names like 'user*name' or 'user(middle)name'

- Prevent the use of zero-length password authentication.  See
  https://github.com/Pylons/pyramid_ldap/pull/13

0.1
---

-  Initial version


