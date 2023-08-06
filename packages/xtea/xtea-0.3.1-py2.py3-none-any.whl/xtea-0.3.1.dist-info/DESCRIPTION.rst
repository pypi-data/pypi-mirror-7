===========
Python XTEA
===========

    This is an XTEA-Cipher implementation in Python (eXtended Tiny Encryption Algorithm).

    XTEA is a blockcipher with 8 bytes blocksize and 16 bytes Keysize (128-Bit).
    The algorithm is secure at 2014 with the recommend 64 rounds (32 cycles). This
    implementation supports following modes of operation:
    ECB, CBC, CFB, OFB, CTR (buggy)


Example:

    >>> from xtea import *
    >>> key = " "*16  # Never use this
    >>> text = "This is a text. "*8
    >>> x = new(key, mode=MODE_OFB, IV="12345678")
    >>> c = x.encrypt(text)
    >>> text == x.decrypt(c)
    True

Note
====

    I does NOT guarantee that this implementation (or the base cipher) is secure. If there are bugs, tell me them on github. Changelog
---------

Version 0.3.1; Jul 11, 2014
~~~~~~~~~~~~~~~~~~~~~~~~~~~

[0.3.1] Minor Fixes

 - Fixed that the length of data will not be checked

Version 0.3.0; Jul 11, 2014
~~~~~~~~~~~~~~~~~~~~~~~~~~~

[0.3.0] Added CFB mode

 - Added CFB mode
 - Fully working with PEP 272
 - Raising NotImplementedError only on PGP-CFB (OpenPGP) mode
 - Wheel support and changelog (0.2.1)

Version 0.2.1 - dev; Jul 10, 2014
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Never released...

 - Added better wheel support for uploading (just for me) with a setup.cfg
 - Added this file (auto uploading on pypi/warehouse and github)
 - (upload.py for github)

Version 0.2.0; Jul 9, 2014
~~~~~~~~~~~~~~~~~~~~~~~~~~

[0.2.0] Added a test feature; warning in CTR

 - Added a test feature
 - Raises warning on CTR, added a handler that CTR will not crash anymore ;) 

Version 0.1.1; Jul 9, 2014
~~~~~~~~~~~~~~~~~~~~~~~~~~

[0.1.1] NotImplementedError on CFB

 - Module raises a NotImplementedError on CFB
 - Minor changes

Version 0.1; Jun 22, 2014
~~~~~~~~~~~~~~~~~~~~~~~~~

[0.1] Initial release

 - Supports all mode except CFB
 - Buggy CTR ( "ß" = "\\xc3\\x9f" )
 - Working with PEP 272, default mode is ECB

