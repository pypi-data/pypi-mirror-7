pystock-crawler
===============

.. image:: https://badge.fury.io/py/pystock-crawler.png
    :target: http://badge.fury.io/py/pystock-crawler

.. image:: https://travis-ci.org/eliangcs/pystock-crawler.png?branch=master
    :target: https://travis-ci.org/eliangcs/pystock-crawler

.. image:: https://coveralls.io/repos/eliangcs/pystock-crawler/badge.png?branch=master
    :target: https://coveralls.io/r/eliangcs/pystock-crawler

``pystock-crawler`` is a utility for crawling stock historical data including:

* Daily prices from `Yahoo Finance`_
* Fundamentals from 10-Q and 10-K filings on `SEC EDGAR`_


Example Output
--------------

Apple's daily prices::

    symbol,date,open,high,low,close,volume,adj_close
    AAPL,2014-04-28,572.80,595.75,572.55,594.09,23890900,594.09
    AAPL,2014-04-25,564.53,571.99,563.96,571.94,13922800,571.94
    AAPL,2014-04-24,568.21,570.00,560.73,567.77,27092600,567.77
    ...

Google's fundamentals::

    symbol,end_date,amend,period_focus,doc_type,revenues,op_income,net_income,eps_basic,eps_diluted,dividend,assets,cur_assets,cur_liab,cash,equity,cash_flow_op,cash_flow_inv,cash_flow_fin
    GOOG,2009-06-30,False,Q2,10-Q,5522897000.0,1873894000.0,1484545000.0,4.7,4.66,0.0,35158760000.0,23834853000.0,2000962000.0,11911351000.0,31594856000.0,3858684000.0,-635974000.0,46354000.0
    GOOG,2009-09-30,False,Q3,10-Q,5944851000.0,2073718000.0,1638975000.0,5.18,5.13,0.0,37702845000.0,26353544000.0,2321774000.0,12087115000.0,33721753000.0,6584667000.0,-3245963000.0,74851000.0
    GOOG,2009-12-31,False,FY,10-K,23650563000.0,8312186000.0,6520448000.0,20.62,20.41,0.0,40496778000.0,29166958000.0,2747467000.0,10197588000.0,36004224000.0,9316198000.0,-8019205000.0,233412000.0
    ...


Installation
------------

Prerequisites:

* Python 2.7

``pystock-crawler`` is based on Scrapy_, so you will also need to install
prerequisites such as lxml_ and libffi_ for Scrapy and its dependencies.

Install with `virtualenv`_ (recommended)::

    pip install pystock-crawler

Or do system-wide installation::

    sudo pip install pystock-crawler


Quickstart
----------

**Example 1.** Google's and Yahoo's daily prices ordered by date::

    pystock-crawler prices GOOG,YHOO -o out.csv --sort

**Example 2.** Daily prices of all companies listed in ``./symbols.txt``::

    pystock-crawler prices ./symbols.txt -o out.csv

**Example 3.** Facebook's fundamentals during 2013::

    pystock-crawler reports FB -o out.csv -s 20130101 -e 20131231

**Example 4.** Fundamentals all companies in ``./nyse.txt`` and direct the
logs to ``./crawling.log``::

    pystock-crawler reports ./nyse.txt -o out.csv -l ./crawling.log


Usage
-----

Type ``pystock-crawler -h`` to see command help::

    Usage:
      pystock-crawler prices <symbols> (-o OUTPUT) [-s YYYYMMDD] [-e YYYYMMDD] [-l LOGFILE] [--sort]
      pystock-crawler reports <symbols> (-o OUTPUT) [-s YYYYMMDD] [-e YYYYMMDD]  [-l LOGFILE] [--sort]
      pystock-crawler (-h | --help)
      pystock-crawler (-v | --version)

    Options:
      -h --help     Show this screen
      -o OUTPUT     Output file
      -s YYYYMMDD   Start date [default: ]
      -e YYYYMMDD   End date [default: ]
      -l LOGFILE    Log output [default: ]
      --sort        Sort the result

Use ``prices`` to crawl price data and ``reports`` to crawl fundamentals.

``<symbols>`` can be an inline string separated with commas or a text file
that lists symbols line by line. For example, the inline string can be
something like ``AAPL,GOOG,FB``. And the text file may look like this::

    # This line is comment
    AAPL    Put anything you want here
    GOOG    Since the text here is ignored
    FB

Use ``-o`` to specify the output file. CSV is the only supported output format
for now.

``-l`` is where the crawling logs go to. If not specified, the logs go to
stdout.

The rows in the output CSV file are in an arbitrary order by default. Use
``--sort`` to sort them by symbols and dates. But if you have a large output
file, don't use ``--sort`` because it will be slow and eat a lot of memory.

**NOTE**: The crawler stores HTTP cache in a directory named ``.scrapy`` under
your current working directory. The cache helps speed up the crawling process
next time your fetch same web pages again. The cache can be quite huge. If you
don't need it, just delete the ``.scrapy`` directory after you've done
crawling.


Developer Guide
---------------

Installing Dependencies
~~~~~~~~~~~~~~~~~~~~~~~
::

    pip install -r requirements.txt


Running Test
~~~~~~~~~~~~

Install ``pytest``, ``pytest-cov``, and ``requests`` if you don't have them::

    pip install pytest pytest-cov requests

Then run the test::

    py.test

This downloads the test data from from `SEC EDGAR`_ on the fly, so it will
take some time and disk space. If you want to delete test data, just delete
``pystock_crawler/tests/sample_data`` directory.


.. _libffi: https://sourceware.org/libffi/
.. _lxml: http://lxml.de/
.. _Scrapy: http://scrapy.org/
.. _SEC EDGAR: http://www.sec.gov/edgar/searchedgar/companysearch.html
.. _virtualenv: http://www.virtualenv.org/
.. _virtualenvwrapper: http://virtualenvwrapper.readthedocs.org/
.. _Yahoo Finance: http://finance.yahoo.com/
