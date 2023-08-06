======================
Stack Overflow Watcher
======================
.. image:: https://travis-ci.org/Matt-Deacalion/Stackoverflow-Watcher.svg?branch=master
    :target: https://travis-ci.org/Matt-Deacalion/Stackoverflow-Watcher

A library for Stack Overflow question notifications written in Python.

Installation
------------
You can install stack-watcher using pip. At the moment it only works on Python 3.4::

    $ pip install stack-watcher

Usage
-----
Here's how to follow the most recent questions on Stack Overflow which have the “python” tag:

.. code-block:: python

    >>> from stack_watcher import Retriever
    >>> retriever = Retriever(tag='python')
    >>> for question in retriever.questions():
    ...    print(question.link)
    ...
    http://stackoverflow.com/questions/24127601/uwsgi-request-timeout-in-python
    http://stackoverflow.com/questions/24127567/python-traceroute-doesnt-work
    http://stackoverflow.com/questions/24127395/web-crawler-url-address-failure
    http://stackoverflow.com/questions/24126915/python-logging-handler-dies
    http://stackoverflow.com/questions/24126663/how-to-disable-a-nosetest-plugin
    http://stackoverflow.com/questions/24126629/fedora-apache-wsgi-python-oracle

This will continue to run and pull in the latest questions until it's killed.
The `question` objects also have the following attributes:

.. code-block:: python

    >>> question.__dict__
    {'question_id': 24126663,
     'title': 'how to disable a nosetest plugin',
     'link': 'http://stackoverflow.com/questions/24126663',
     'creation_date': 1402339020,
     'tags': ['python', 'nose', 'nosetests'],
     'score': 2,
     'view_count': 10,
     'answered': False,
     'owner_display_name': 'ftravers',
     'owner_link': 'http://stackoverflow.com/users/408489/ftravers',
     'owner_id': 408489,
     'owner_reputation': 966,
     'owner_accept_rate': 50}

Licence
-------
Copyright © 2014 `Matt Deacalion Stevens`_, released under The `MIT License`_.

.. _Matt Deacalion Stevens: http://dirtymonkey.co.uk
.. _MIT License: http://deacalion.mit-license.org
