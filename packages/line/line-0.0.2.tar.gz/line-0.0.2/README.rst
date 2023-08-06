LINE
====

`|PyPi version| <https://crate.io/packages/line/>`_ `|PyPi
downloads| <https://crate.io/packages/line/>`_

May the LINE be with you...

::

    >>> from line import LineClient
    >>> client = LineClient("carpedm20", "xxxxxxxxxx")
    Enter PinCode '9779' to your mobile phone in 2 minutes
    >>> client = LineClient("carpedm20@gmail.com", "xxxxxxxxxx")
    Enter PinCode '7390' to your mobile phone in 2 minutes
    >>> print client.getProfile()

Installing
----------

First, you need to install **Apache Thrift**. Install instructions are
`here <http://thrift.apache.org/docs/install/>`_. (This might take some
time...)

Next:

::

    $ pip install line

Or, you can use:

::

    $ easy_install line 

Or, you can also install manually:

::

    $ git clone git://github.com/carpedm20/line.git
    $ cd LINE
    $ python setup.py install

Using
-----

First, you need to create a ``LineClinet`` object with ``YOUR_ID`` and
``YOUR_PASSWORD``. ``YOUR ID`` can be ``LINE email`` address or
``NAVER id``.

::

    >>> from line import LineClient
    >>> client = LineClient(YOUR_ID, YOUR_PASSWORD)
    Enter PinCode '9779' to your mobile phone in 2 minutes

After you enter ``PinCode`` to your mobile phone, you will get
``authToken``.

::

    >>> authToken = client.authToken
    >>> print authToken

With ``authToken``, you don't have to enter ``PinCode`` to your phone
anymore!

::

    >>> client = LineClient(authToken=authToken)
    >>> print client.getProfile()

Screenshot
----------

.. figure:: http://3.bp.blogspot.com/-FX3ONLEKBBY/U9xJD8JkJbI/AAAAAAAAF2Q/1E7VXOkvYAI/s1600/%E1%84%89%E1%85%B3%E1%84%8F%E1%85%B3%E1%84%85%E1%85%B5%E1%86%AB%E1%84%89%E1%85%A3%E1%86%BA+2014-08-02+%E1%84%8B%E1%85%A9%E1%84%8C%E1%85%A5%E1%86%AB+10.47.15.png%20
   :align: center
   :alt: alt\_tag

License
-------

Source codes are distributed under BSD license.

Author
------

Taehoon Kim / `@carpedm20 <http://carpedm20.github.io/about/>`_

.. |PyPi version| image:: https://pypip.in/v/line/badge.png
.. |PyPi downloads| image:: https://pypip.in/d/line/badge.png
