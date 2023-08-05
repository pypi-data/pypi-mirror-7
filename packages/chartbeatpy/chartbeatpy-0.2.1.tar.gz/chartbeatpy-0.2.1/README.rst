Chartbeatpy
===========

A simple, synchronous charbeat API wrapper.  
This python package creates a simple "pythonic" entry point
for the Chartbeat API.  Originally created by Timothee Peignier,
we are adapting it to our needs here at Detroit Media Partnership.

Any requests, issues should be directed towards us in this forked 
repository, or email me at neurosnap@gmail.com

Chartbeat API Explorer_

.. _Explorer: https://chartbeat.com/docs/api/explore/

Installation
------------

To install charbeatpy, use pip:

.. code:: bash

    $ pip install chartbeat

or 

.. code:: bash

    $ python setup.py install

Quick How To
------------

.. code:: python

    from chartbeatpy import Chartbeat

    beat = Chartbeat("<your chartbeat api key>", "<your host>")
    # live data
    beat.quickstats()
    beat.geo()
    # some API endpoints require extra parameters
    beat.histogram(keys=[user,title], breaks=[1,2,10])
    beat.path_summary(keys=[pagetimer, time_spent, new])
    beat.summary(keys=[domain, title, read, write, idle])
    beat.recent()
    beat.referrers()
    beat.top_pages()

    # historical data
    beat.engage_series()
    beat.engage_stats()
    beat.social_series()
    beat.social_stats()
    beat.traffic_series()
    beat.traffic_stats()

    # specify API version number
    oldbeat = Chartbeat("<API>", "<host>", 2)
    oldbeat.quickstats()


