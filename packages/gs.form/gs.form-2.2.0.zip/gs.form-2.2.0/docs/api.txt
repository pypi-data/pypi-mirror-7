:mod:`gs.form` API Reference
============================

The package exports the following API symbol.

.. autofunction:: gs.form.post_multipart

Internals
---------

In addition to the :func:`post_multipart` function, the following
are used internally.

.. autoclass:: gs.form.postmultipart.Connection
   :members:

.. autofunction:: gs.form.postmultipart.encode_multipart_formdata

.. autofunction:: gs.form.postmultipart.get_content_type
