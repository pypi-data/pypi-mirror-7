js.url_parser
*************

Introduction
============

This library packages `url-parser`_ for `fanstatic`_.

.. _`fanstatic`: http://fanstatic.org
.. _`url-parser`: https://github.com/MadeByMike/url-parser

This requires integration between your web framework and ``fanstatic``,
and making sure that the original resources (shipped in the ``resources``
directory in ``js.url_parser``) are published to some URL.


How to use?
===========

This should be setup before rendering a page. See `fanstatic`_ for more
information::

  >>> from fanstatic import init_needed
  >>> needed = init_needed(base_url='http://localhost')

You can import ``url_parser`` from ``js.url_parser`` and ``need`` it where you want
these resources to be included on a page::

  >>> from js.url_parser import url_parser
  >>> url_parser.need()

Render the inclusion::

  >>> print needed.render()
  <script type="text/javascript" src="http://localhost/fanstatic/url-parser/url-parser.js"></script>

CHANGES
*******

1.1.0 (unreleased)
===============================

- Initial release.


