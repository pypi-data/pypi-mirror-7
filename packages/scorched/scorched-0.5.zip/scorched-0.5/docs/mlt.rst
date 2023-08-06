.. _mlt:

More Like This queries
======================

More Like This (MLT) is a feature of Solr which provides for comparisons of
documents; you can ask Solr to tell you about any More documents it has that
are Like This one.

An MLT query can be part of a standard query (see
:ref:`standard-query-more-like-this`.), in which case you're asking Solr to
tell you not only about immediate query results, but also about any other
results which are similar to the results you've got.

Alternatively, you can feed Solr an entire document that is not already in its
index, and ask to do an MLT query on that document.

The first case is covered above in :ref:`standard-query-more-like-this`; the
second case we'll show here.

Basic MLT query
---------------

Instead of calling the ``query`` method on the interface, we call the
``mlt_query`` method.

::

    >>> si.mlt_query(fields="name", content=open("localfile").read())

We give the MLT handler some content (sourced in this case from a local file);
the MLT query will take this text, analyze it, and retrieve documents that are
similar according to the results of its analysis.

The results are returned in the same format as illustrated in the ``mlt()``
method.

Further MLT query options
-------------------------

If we wanted similarity to be calculated with respect to a different field or
fields.:

::

    >>> si.mlt_query(content=open("localfile").read(),
    ...              fields=["name", "author_t"])

We can understand a little more about why we get the results we do by asking
for the result of the MLT document analysis.

::

    >>> si.mlt_query(fields="name", content=open("localfile").read(),
    ...              interestingTerms="list")
    >>> si.mlt_query(fields="name", content=open("localfile").read(),
    ...              interestingTerms="details")

"list" will return a list of the interesting terms extracted; "details" will
also provide details of the boost used for each term.

If the document you're supplying is not encoded in UTF-8 (or equivalently
ASCII) format, then you need to specify the charset in use (using the list
available at http://docs.python.org/library/codecs.html#standard-encodings:

::

    >>> si.mlt_query(fields="name", content=open("localfile").read(),
    ...              content_charset="iso-8859-1")

Sourcing content from the web
-----------------------------

You can also choose to tell Solr to source the document from the web, by giving
the URL for the content rather than supplying it yourself:

::

    >>> si.mlt_query(fields="name", url="http://example.com/document")

All the other options above still apply to URL-sourced content, except for
"content_charset"; that's up to the webserver where the content is stored.

In all the cases above, you can also specify any of the other options shown in
``mlt()``, apart from "count".

MLT queries on indexed content
------------------------------

You can perform an MLT query on indexed content in the following way:

::

    >>> res = si.mlt_query("genre_s", interestingTerms="details",
    ...                    mintf=1, mindf=1).query(
    ...                    id="978-0641723445").execute()
    >>> res.result.docs
    [{u'_version_': 1462917302263480320,
      u'author': u'Rick Riordan',
      u'author_s': u'Rick Riordan',
      u'cat': [u'book', u'paperback'],
      u'genre_s': u'fantasy',
      u'id': u'978-1423103349',
      u'inStock': True,
      u'name': u'The Sea of Monsters',
      u'pages_i': 304,
      u'price': 6.49,
      u'price_c': u'6.49,USD',
      u'sequence_i': 2,
      u'series_t': u'Percy Jackson and the Olympians'},
     {u'_version_': 1462917302263480321,
      u'author': u'Jostein Gaarder',
      u'author_s': u'Jostein Gaarder',
      u'cat': [u'book', u'paperback'],
      u'genre_s': u'fantasy',
      u'id': u'978-1857995879',
      u'inStock': True,
      u'name': u"Sophie's World : The Greek Philosophers",
      u'pages_i': 64,
      u'price': 3.07,
      u'price_c': u'3.07,USD',
      u'sequence_i': 1}]
    >>> res.interesting_terms
    >>> [u'genre_s:fantasy', 1.0]

ie - initialize an otherwise empty mlt_query object, and then run queries on it
as you would run normal queries. The full range of query operations is
supported when composing the query for indexed content:

::

    >>> si.mlt_query("name").query(title='Whale').query(~si.Q(
    ...     author='Melville').query(si.Q('Moby') | si.Q('Dick'))

Chaining MLT queries
--------------------

The ``mlt_query()`` method is chainable in the same way as the ``query``
method. There are a fre differences to note.

* You can't chain a ``query()`` onto an ``mlt_query()`` call
  if the MLT query is based on supplied ``content`` or ``url``.
* You can't chain multiple ``mlt_query()`` methods together - only one content
  source can be considered at a time.

The ``mlt_query()`` method takes all of the mlt() options except "count".
