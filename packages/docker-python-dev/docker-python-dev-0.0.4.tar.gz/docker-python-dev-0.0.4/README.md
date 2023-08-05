# Docker python developer tools (a.k.a. "dpy")

This is a collection of tools meant to ease life of docker python workers.
Right now, this is work in progress.

[![PyPI version][pypi-image]][pypi-url]
[![Build Status][travis-image]][travis-url]
[![Coverage Status][coveralls-image]][coveralls-url]

## Installation

`pip install docker-python-dev`

## Usage

 * all commands support an additional `-d PATH` argument
 * `dpy sanity`: sanity check the docker python project
 * `dpy style`: style check the docker python project
 * `dpy test`: test the docker python project
 * `dpy test-all`: test all python version the docker python project

If you want to create a new storage driver for `docker-registry`:

 * `dpy-driver new`


## License

This is licensed under the Apache license.

[pypi-url]: https://pypi.python.org/pypi/docker-python-dev
[pypi-image]: https://badge.fury.io/py/docker-python-dev.svg

[travis-url]: http://travis-ci.org/dmp42/docker-python-dev
[travis-image]: https://secure.travis-ci.org/dmp42/docker-python-dev.png?branch=master

[coveralls-url]: https://coveralls.io/r/dmp42/docker-python-dev
[coveralls-image]: https://coveralls.io/repos/dmp42/docker-python-dev/badge.png?branch=master

