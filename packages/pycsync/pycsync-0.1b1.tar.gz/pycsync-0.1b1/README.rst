=======
Pycsync
=======

.. image:: https://travis-ci.org/shadowfax-chc/pycsync.svg
    :target: https://travis-ci.org/shadowfax-chc/pycsync
    :alt: Build Status

.. image:: https://coveralls.io/repos/shadowfax-chc/pycsync/badge.png
    :target: https://coveralls.io/r/shadowfax-chc/pycsync
    :alt: Coverage Status

.. image:: https://landscape.io/github/shadowfax-chc/pycsync/master/landscape.png
    :target: https://landscape.io/github/shadowfax-chc/pycsync/master
    :alt: Code Health

.. image:: https://gemnasium.com/shadowfax-chc/pycsync.svg
    :target: https://gemnasium.com/shadowfax-chc/pycsync
    :alt: Dependency Status

.. image:: https://pypip.in/v/pycsync/badge.png
    :target: https://pypi.python.org/pypi/pycsync/
    :alt: Pypi Version

.. image:: https://pypip.in/d/pycsync/badge.png
    :target: https://pypi.python.org/pypi/pycsync/
    :alt: Pypi Downloads

Sync pictures between filesystem and Flickr

Install
-------

This uses the python_flickr_api_.

To install latest::

    pip install pycsync


Usage
-----

First oauth needs to be setup for the application::

    pycsync -a

    Please visit to get an verifier code:
    ---------------------------------
    http://www.flickr.com/services/oauth/authorize?oauth_token=<token>&perms=write
    ---------------------------------
    Please input the verifier code here:

Then copy the link to a browser. After authorizing pycsync, the browser should
display something like::

    <rsp stat="ok">
      <method>flickr.test.echo</method>
      <api_key>key</api_key>
      <oauth_token>token</oauth_token>
      <oauth_verifier>verifer</oauth_verifier>
    </rsp>

Where ``key`` is pycsync's api key, ``token`` is the oauth token from above,
and ``verifier`` is the verifier key for further authentication. Copy the
``verifier`` and input it to pycsync.

``NOTE:`` pycsync can either be run from the sync directory or the directory
can be specified with the ``-p`` option.

Now to sync simply run::

    pycsync


Limitations
-----------

1. Flickr stores photos in albums. There is no concept of a sub-album. Thus
   this requires a flat file structure for the local files. The file system
   layout must contain one level of directories with files in them. The
   directories will be mapped to Albums. Any subdirectories will be ignored.
   Also any top-level files will be ignored.


.. _python_flickr_api: https://github.com/alexis-mignon/python-flickr-api
