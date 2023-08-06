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
    text = 'I love ☀'
    encoded_text = moji.encode(text)           # encoded_text = u'I love [:sunny]'
    decoded_text = moji.decode(encoded_text)   # decoded_text = u'I love ☀''


Resources Support
-----------------

`Emoji Categories <http://emojipedia.org/>`_

`Emoji Unicode Tables <http://apps.timwhitlock.info/emoji/tables/unicode>`_
