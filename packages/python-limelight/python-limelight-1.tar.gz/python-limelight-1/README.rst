|build| |downloads| |license|

Python-LimeLight
================

A pythonic Lime Light API wrapper.

We currently support only a subset of the full Lime Light API functionality, we will be adding
methods and plan to achieve total coverage some time during the next several months.

``python-limelight`` contains two modules that implement the two APIs that Lime Light exposes. Lime
Light calls these APIs their Transaction and Membership APIs, we've implemented them as
``limelight.transaction`` and ``limelight.membership``. Both are essentially an 1:1 mapping of
pythonic-as-possible functions to API methods. Unfortunately, Lime Light's API is pretty much all
over the place. It's comprehensive and useful, but not well organized or consistent.

Our solution is designed for both flexibility and ease of use: the entire API is exposed in python
in the aforementioned modules and is used as machinery for a much more cohesive interface to the
CRM.

.. |build| image:: https://travis-ci.org/heropunch/python-limelight.svg
   :target: https://travis-ci.org/heropunch/python-limelight
   :alt: Travis-CI

.. |license| image:: https://pypip.in/license/python-limelight/badge.png
   :target: https://pypi.python.org/pypi/python-limelight/
   :alt: License

.. |downloads| image:: https://pypip.in/download/python-limelight/badge.png
   :target: https://pypi.python.org/pypi/python-limelight/
   :alt: Downloads
