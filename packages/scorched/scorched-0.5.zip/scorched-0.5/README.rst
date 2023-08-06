Scorched
========

Scorched is a sunburnt offspring and like all offspring it tries to make
things better or at least different.

Git Repository and issue tracker: https://github.com/lugensa/scorched
Documentation: http://scorched.readthedocs.org/en/latest/

.. |travisci| image::  https://travis-ci.org/lugensa/scorched.png
.. _travisci: https://travis-ci.org/lugensa/scorched

.. image:: https://coveralls.io/repos/lugensa/scorched/badge.png
    :target: https://coveralls.io/r/lugensa/scorched 

|travisci|_

.. _Solr : http://lucene.apache.org/solr/
.. _Lucene : http://lucene.apache.org/java/docs/index.html


Following some major differences:

- No validation of queries in client code (make code much more lightweight)

- Send and receive as json. (Faster 20k docs from 6.5s to 1.3s)

- API is more lightweight e.g. ``add`` consums now only dicts.

- Wildcard search strings need to be explicitly set.

- Python 3

- ...


Local testing
=============

First checkout the sources::

  https://github.com/lugensa/scorched.git

Now create a virtual-env and install some dependencies::

  cd scorched
  virtualenv ./
  bin/pip install -e .

Start the solr server to test against::

  # DEBUG=1|0: verbose output of solr server on|off
  # SOLR_VERSION=x.y.z (the version to test against)
  # the solr startup script reports the pid of the solr process
  SOLR_VERSION=4.6.1 SOLR_PORT=44177 DEBUG=1 SOLR_CONFS="scorched/tests/solrconfig.xml" ./testing-solr.sh
  
  # stop solr
  kill -9 $pid

Running the tests::

  SOLR_URL=http://localhost:44177/solr ./bin/nosetests -s scorched
