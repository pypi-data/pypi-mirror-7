Process runner inspired by foreman
==================================

You should use it during development.


Usage
-----

Create a `Henfile` (it is YAML):

.. code:: yaml

    name: Shopium[dev]
    proc:
        web: "python -u ./manage.py runserver -b 0.0.0.0"
        cdn: "python -u ./dev_cdn_server.py"
        solr: "./run_solr"
        workers: "python -u ./manage.py runworkers"
        smtp_worker: "sh -c \"PYTHONPATH=libs:core python workers/smtp_gateway.py  shopium.ini\""
    env:
        PYTHONUNBUFFERED: "1"


Run `hen`:

.. code:: sh

    hen


Running with some processes disabled:

.. code:: sh

    hen --nocdn --nosolr


Installation
------------

.. code:: sh

    pip install hen


Compatibility
-------------

Tested with Python 2.7 and Python 3.2/3.3


How to contribute
-----------------

It is easy. Fork repo on GitHub, fix stuff and send me nice looking pull-request.
