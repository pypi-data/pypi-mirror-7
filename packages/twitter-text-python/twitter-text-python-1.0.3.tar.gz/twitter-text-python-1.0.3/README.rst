twitter-text-python
===================

**twitter-text-python** is a Tweet parser and formatter for Python. Extract users, hashtags, URLs and format as HTML for display.


PyPI release:
http://pypi.python.org/pypi/twitter-text-python/

The current version was forked by Edmond Burnett in July 2014:
https://github.com/edburnett/twitter-text-python

The library was forked by Ian Ozsvald in January 2013 and released to PyPI, some bugs were fixed, a few minor changes to functionality added (no longer supported):
https://github.com/ianozsvald/twitter-text-python

The original ttp comes from Ivo Wetzel (no longer supported):
https://github.com/BonsaiDen/twitter-text-python

It is based on twitter-text-java_ and did pass all the unittests of 
twitter-text-conformance_ plus some additional ones. Note that the conformance tests are now behind (easy PR for someone to work on: https://github.com/ianozsvald/twitter-text-python/issues/5 ):

.. _twitter-text-java: http://github.com/mzsanford/twitter-text-java
.. _twitter-text-conformance: http://github.com/mzsanford/twitter-text-conformance



Usage
-----

    >>> from ttp import ttp
    >>> p = ttp.Parser()
    >>> result = p.parse("@ianozsvald, you now support #IvoWertzel's tweet parser! https://github.com/ianozsvald/")
    >>> result.reply
    'ianozsvald'
    >>> result.users
    ['ianozsvald']
    >>> result.tags
    ['IvoWertzel']
    >>> result.urls
    ['https://github.com/ianozsvald/']
    >>> result.html
    u'<a href="http://twitter.com/ianozsvald">@ianozsvald</a>, you now support <a href="http://search.twitter.com/search?q=%23IvoWertzel">#IvoWertzel</a>\'s tweet parser! <a href="https://github.com/ianozsvald/">https://github.com/ianozsvald/</a>'

If you need different HTML output just subclass and override the ``format_*`` methods.

You can also ask for the span tags to be returned for each entity::

    >>> p = ttp.Parser(include_spans=True)
    >>> result = p.parse("@ianozsvald, you now support #IvoWertzel's tweet parser! https://github.com/ianozsvald/")
    >>> result.urls
    [('https://github.com/ianozsvald/', (57, 87))]


To use the shortlink follower:

    >>> from ttp import utils
    >>> # assume that result.urls == ['http://t.co/8o0z9BbEMu', u'http://bbc.in/16dClPF']
    >>> print utils.follow_shortlinks(result.urls)  # pass in list of shortlink URLs
    {'http://t.co/8o0z9BbEMu': [u'http://t.co/8o0z9BbEMu', u'http://bbc.in/16dClPF', u'http://www.bbc.co.uk/sport/0/21711199#TWEET650562'], u'http://bbc.in/16dClPF': [u'http://bbc.in/16dClPF', u'http://www.bbc.co.uk/sport/0/21711199#TWEET650562']}
     >>> # note that bad shortlink URLs have a key to an empty list (lost/forgotten shortlink URLs don't generate any error)


Installation
------------

pip and easy_install will do the job::

    # via: http://pypi.python.org/pypi/twitter-text-python
    $ pip install twitter-text-python  
    $ python
    >>> from ttp import ttp
    >>> ttp.__version__
    '1.0.0.2'

Changelog
---------

 * 2013/2/11 1.0.0.2 released to PyPI
 * 2013/6/1 1.0.1 new working version, adding comma parse fix (thanks https://github.com/muckrack), used autopep8 to clean the src, added a shortlink expander


Tests
-----

Checkout the code via github https://github.com/edburnett/twitter-text-python and run tests locally::

    $ python ttp/tests.py 
    ....................................................................................................
    ----------------------------------------------------------------------
    Ran 100 tests in 0.009s
    OK


Contributing
------------

The source is available on GitHub_, to
contribute to the project, fork it on GitHub and send a pull request.
Everyone is welcome to make improvements to **twp**!

.. _GitHub: https://github.com/edburnett/twitter-text-python


Todo
----

  * Consider adding capitalised phrase identification
  * Consider adding a repeated-char remover (e.g. grrrrrrr->grr)
  * Make it 1 line to parse and get a results dict via __init__.py
  * Tag the next release

Doing a release
---------------

In parent directory on Edmond's machine see USE_THIS_FOR_PYPI_RELEASE.txt. The short form::

    $ # edit setup.py to bump the version number
    $ git tag -a v1.0.1 -m 'v1.0.1 release'
    $ git push origin --tags
    $ twitter-text-python $ python setup.py sdist --formats=gztar,zip register upload -r http://pypi.python.org/pypi
    $ # this uses ~/.pypirc with cached login details


License
-------

*MIT*

Copyright (c) 2012 Ivo Wetzel.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Copyright (c) 2010-2013 Ivo Wetzel

