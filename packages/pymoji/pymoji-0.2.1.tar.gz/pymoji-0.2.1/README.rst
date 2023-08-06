Pymoji
------

A emoji converter between unicode and ascii text.

Install & Usage
~~~~~~~~~~~~~~~
::

    pip install pymoji

::

    from pymoji import PyMoji
    moji = PyMoji()
    text = 'hello ☀ !'
    encoded_text = moji.encode(text)           # u'hello [:sunny]!'
    decoded_text = moji.decode(encoded_text)   # u'hello ☀ !'


External Resources
~~~~~~~~~~~~~~~~~~

* `Emoji Categories <http://emojipedia.org/>`_
* `Emoji Unicode Tables <http://apps.timwhitlock.info/emoji/tables/unicode>`_
