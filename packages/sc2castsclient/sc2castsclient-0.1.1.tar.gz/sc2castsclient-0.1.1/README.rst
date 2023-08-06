===============================
sc2casts client
===============================

.. image:: https://badge.fury.io/py/sc2castsclient.png
    :target: http://badge.fury.io/py/sc2castsclient

.. image:: https://travis-ci.org/thmttch/sc2castsclient.png?branch=master
    :target: https://travis-ci.org/thmttch/sc2castsclient

.. image:: https://pypip.in/d/sc2castsclient/badge.png
    :target: https://crate.io/packages/sc2castsclient?version=latest

Client for crawling sc2casts.com, in python

* Free software: BSD license
* Documentation: http://sc2castsclient.rtfd.org.

This thing needs a lot of work.

Features
--------

* TODO

Usage
--------

Set what the Makefile provides:

```bash
$> make help
```

Run tests:

```bash
# quick dev testing
$> make test

# full testing
$> make testall
```

Development
--------

There is a [`download script`](tests/data/download.sh) for updating the local
test suite, for keeping up-to-date as [sc2casts.com](https://sc2casts.com)
changes over time. Note that the script is meant to be run in the same dir:

```bash
$> cd tests/data && ./download.sh
```

Misc
--------

Packaged with the help of https://github.com/audreyr/cookiecutter-pypackage
