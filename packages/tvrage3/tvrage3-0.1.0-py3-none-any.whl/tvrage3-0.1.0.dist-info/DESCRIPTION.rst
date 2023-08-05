===============================
tvrage3
===============================

.. image:: https://badge.fury.io/py/tvrage3.png
    :target: http://badge.fury.io/py/tvrage3

.. image:: https://travis-ci.org/kalind/tvrage3.png?branch=master
        :target: https://travis-ci.org/kalind/tvrage3

.. image:: https://pypip.in/d/tvrage3/badge.png
        :target: https://pypi.python.org/pypi/tvrage3


Python3 client for accessing tv show information from www.tvrage.com

* Free software: BSD license
* Documentation: http://tvrage3.rtfd.org.

Features
--------

* Lazy, you can search tvrage with quick-search and still get all the
  information as you would get with a full search about the specified show.
  When a Show object is asked to return information not provided by
  the search method used, it will query tvrage for the information.

* Will handle the occasional database errors and information inconsistencies
  in the tvrage database sane and gracefully.

* High-level api, handles all the XML stuff for you.


Usage
--------

* Searching

  * Full search

    Returns a list of Show objects.

    .. code-block:: python

       from tvrage3.search import search
       results = search('Buffy')
       first = results[0]
       first.name # => 'Buffy the Vampire Slayer'

  * Quick search

    Returns a show object, the closest match to search term or None.

    .. code-block:: python

       from tvrage3.search import quick_info
       result = quick_info('Csi crime')
       result.name # => 'CSI: Crime Scene Investigation'

       # Enable stricter matching
       result = quick_info('CSI crime', exact=True)
       result == None # => True

  * Search by id

    Returns a Show object, or None if id is incorrect.

    .. code-block:: python

       from tvrage3.search import search_id
       result = search_id('2930')
       result.name # => 'Buffy the Vampire Slayer'

* Show objects

  Show objects should not be initialized manually, it should be done by one of
  the search functions, but for this example we do.

  .. code-block:: python

     from tvrage3.api import Show
     show = Show(show_id='3183')

     show.air_day        # => 'Wednesday'
     show.air_time       # => '22:00'
     show.classification # => 'Scripted'
     show.country        # => 'US'
     show.ended_year     # => None
     show.genres         # => ['Action', 'Crime', 'Drama']
     show.link           # => 'http://www.tvrage.com/CSI'
     show.name           # => 'CSI: Crime Scene Investigation'
     show.network        # => OrderedDict([('@country', 'US'), ('#text', 'CBS')])
     show.runtime        # => 60
     show.seasons        # => 14
     show.show_id        # => '3183'
     show.started_year   # => 2000
     show.status         # => 'Returning Series'




History
-------

0.1.0 (2014-05-10)
++++++++++++++++++

* First release on PyPI.


