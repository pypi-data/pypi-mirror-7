===========
``gs.form``
===========
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Submit a form to a Web server using a ``POST``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Author: `Michael JasonSmith`_
:Contact: Michael JasonSmith <mpj17@onlinegroups.net>
:Date: 2014-05-05
:Organization: `GroupServer.org`_
:Copyright: This document is licensed under a
  `Creative Commons Attribution-Share Alike 4.0 International License`_
  by `OnlineGroups.Net`_.

Introduction
============

This product contains the core functions and classes for making
HTTP ``POST`` requests to send data to forms. For the most part
it consists of the `post_multipart`_ utility, for posting data to
a form.

While originally written for GroupServer_, there is nothing
specific to GroupServer in this product.

``post_multipart``
==================

The ``gs.form.post_multipart`` function is used to post data to a
form::

  post_multipart(host, selector, fields, files=[], usessl=False)

See the documentation for more on how to use this function.

Acknowledgements
================

The post_multipart_ code was based on `a Python recipe by Wade
Leftwich`_. It was changed to use ``email.multipart`` to create
the multipart document that is sent using a ``POST``.

The Python standard library currently lacks a module for making a
``POST`` to a Web server. `Issue 3244`_ tracks the inclusion of a
module into the standard library.


Resources
=========

- Documentation: http://gsform.readthedocs.org/
- Code repository: https://source.iopen.net/groupserver/gs.form
- Questions and comments to http://groupserver.org/groups/development
- Report bugs at https://redmine.iopen.net/projects/groupserver

.. _GroupServer: http://groupserver.org/
.. _GroupServer.org: http://groupserver.org/
.. _OnlineGroups.Net: https://onlinegroups.net
.. _Michael JasonSmith: http://groupserver.org/p/mpj17
.. _Creative Commons Attribution-Share Alike 4.0 International License:
    http://creativecommons.org/licenses/by-sa/4.0/
.. _a Python recipe by Wade Leftwich: http://code.activestate.com/recipes/146306-http-client-to-post-using-multipartform-data/
.. _Issue 3244: http://bugs.python.org/issue3244
