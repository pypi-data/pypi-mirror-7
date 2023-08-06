nlist
=====
|travis| |space| |coveralls| |space| |license| |space| |version|

.. |space| unicode:: 0x200B
.. |travis| image:: http://img.shields.io/travis/swarmer/nlist.png
.. |coveralls| image:: http://img.shields.io/coveralls/swarmer/nlist.png
.. |license| image:: http://img.shields.io/badge/license-MIT-blue.png
.. |version| image:: http://img.shields.io/pypi/v/nlist.png

nlist is a lightweight multidimensional list in Python.

nlist supports Python 3.4+.


Example code
------------
::

    from nlist import NList

    l = NList([[1, 2], [3, 4]])
    l[1, 0] = '42'
    print(l.index('42')) #=> (1, 0)


Documentation
-------------
`<http://nlist.readthedocs.org/>`_


Installation
------------
``pip install nlist``

Or just grab ``nlist.py``.


License
-------
MIT (see LICENSE.txt)
