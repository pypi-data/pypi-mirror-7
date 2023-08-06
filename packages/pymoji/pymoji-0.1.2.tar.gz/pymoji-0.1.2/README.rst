Pymoji
------

Converter between Emoji Unicode and Ascii Text.

Install
-------
::

    pip install pymoji


Example Usage
-------------
::

    from pymoji import PyMoji
    moji = PyMoji()
    text = 'hello 😀  !'
    encoded_text = moji.encode(text)           # u'hello [:grinning]  !'
    decoded_text = moji.decode(encoded_text)   # u'hello 😀  !'


External Resources
------------------

`Emoji Categories <http://emojipedia.org/>`_

`Emoji Unicode Tables <http://apps.timwhitlock.info/emoji/tables/unicode>`_
