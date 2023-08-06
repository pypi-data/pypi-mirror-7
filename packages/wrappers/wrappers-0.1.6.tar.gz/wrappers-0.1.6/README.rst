========
Wrappers
========

wrappers provide convenient wrappers around existing modules that I use on a regular basis.

storage
=======

Storage class that extends dict to provide attribute access to keys/

ssl
===

Patches ssl.wrap_socket() to use TLSv1 instead of SSLv23 to resolve connection issues.
Details: http://stackoverflow.com/a/24166498/41957::

    from wrappers import ssl

pq
==

pq.PQ() - wrapper around the pyquery.PyQuery constructor that supports mixed-case XML tags.


logger
======

Performs the basicConfig() setup and uses/parses LOG_LEVEL from the environment.

Provides getLogger().

clock
=====

Provides stopwatch-like functionality in a Clock class.
