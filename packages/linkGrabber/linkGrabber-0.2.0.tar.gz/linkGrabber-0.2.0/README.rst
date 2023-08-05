=====
Link Grabber
=====

Link Grabber provides a quick and easy way to grab links from
a single web page.  This python package is a simple wrapper 
around BeautifulSoup_, focusing on grabbing HTML's 
hyperlink tag, "a." 

.. _BeautifulSoup: http://www.crummy.com/software/BeautifulSoup/

.. _find_all: http://www.crummy.com/software/BeautifulSoup/bs4/doc/#find-all

pypi_

.. _pypi: https://pypi.python.org/pypi/linkGrabber/

GitHub_

.. _GitHub: https://github.com/detroit-media-partnership/link-grabber

Dependecies:

*  BeautifulSoup

How-To
======

.. code:: bash

    $ python setup.py install

OR

.. code:: bash

    $ pip install linkGrabber

Quickie
=======

.. code:: python

    import re
    import linkGrabber

    seek = linkGrabber.Links("http://www.google.com")
    seek.find()
    # limit the number of "a" tags to 5
    seek.find(limit=5)
    # filter the "a" tag href attribute
    seek.find({ "href": re.compile("plus.google.com") })

Documentation
=============

find_links
----------

Parameters: 
 *  filters (dict): Beautiful Soup's filters as a dictionary
 *  limit (int):  Limit the number of links in sequential order
 *  reverse (bool): Reverses how the list of <a> tags are sorted
 *  sort (function):  Accepts a function that accepts which key to sort upon
    within the List class

Find all links that have a style containing "11px"

.. code:: python

    import re
    from linkGrabber import Links

    seek = Links("http://www.google.com")
    seek.find({ "style": re.compile("11px")  }, 5)

Reverse the sort before limiting links:

.. code:: python

    from linkGrabber import Links

    seek = Links("http://www.google.com")
    seek.find(limit=2, reverse=True)

Sort by Links property:

.. code:: python

    from linkGrabber import Links

    seek = Links("http://www.google.com")
    seek.find(limit=3, sort=lambda key: key.text)

Link Dictionary
---------------

Currently only three properties exist: 
 *  text (text inbetween the <a></a> tag)
 *  href (href attribute, aka the hyperlink)
 *  seo (parse all text after last "/" in URL and make it human readable)
