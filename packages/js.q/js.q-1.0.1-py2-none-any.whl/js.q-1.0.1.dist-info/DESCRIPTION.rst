js.q
****

Introduction
============

This library packages `q`_ for `fanstatic`_.

.. _`fanstatic`: http://fanstatic.org
.. _`q`: http://documentup.com/kriskowal/q/

This requires integration between your web framework and ``fanstatic``,
and making sure that the original resources (shipped in the ``resources``
directory in ``js.q``) are published to some URL.


How to use?
===========


This should be setup before rendering a page. See `fanstatic`_ for more
information::

  >>> from fanstatic import init_needed
  >>> needed = init_needed(base_url='http://localhost')

You can import ``q`` from ``js.q`` and ``need`` it where you want
these resources to be included on a page::

  >>> from js.q import q
  >>> q.need()

Render the inclusion::

  >>> print needed.render()
  <script type="text/javascript" src="http://localhost/fanstatic/q/q.js"></script>

CHANGES
*******

1.0.1 (2014-09-02)
===============================

- Initial release.


