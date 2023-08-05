# Docker registry {{driver.name}} driver

This is a [docker-registry backend driver](https://github.com/dotcloud/docker-registry/tree/master/depends/docker-registry-core) based on the [{product.name}]({{product.url}}) storage.

[![PyPI version][pypi-image]][pypi-url]
[![Build Status][travis-image]][travis-url]

## Usage

Assuming you have a working docker-registry and your {{product.name}} is setup.

`pip install docker-registry-driver-{{driver.name}}`

Edit your configuration so that `storage` reads `{{driver.name}}`.


## Options

You may add any of the following to your main docker-registry configuration to further configure it.


Example:
```yaml
```

## Problems?

Open a ticket here, including the output of the following commands and informations:

 * are you running the registry from the official docker image? (yes/no)
 * if not:
   * `pip freeze | grep docker`
   * `python --version`
 * the command-line you used to launch the registry
 * if you are not using the vanilla docker-registry configuration file, a complete copy of your configuration file

## Developer setup

Clone this repository.

Get your python ready:

```
sudo apt-get install python-pip
sudo pip install tox
```

You are ready to hack.

Now, verify that what you did is ok:
 * run `python setup.py nosetests` to run tests against your system python
 * run `flake8` to verify that your style is ok
 * run `tox` to verify that your tests pass for all recommended python versions (you might need to install old python versions for this). If you can't, or won't, travis will do that for you when you commit.

Note that a base test suite is provided by [`docker-registry-core`](https://github.com/dotcloud/docker-registry/tree/master/depends/docker-registry-core), hence you won't find these tests in the driver codebase itself.


## License

This is licensed under the Apache license.
Most of the code here comes from docker-registry, under an Apache license as well.

[pypi-url]: https://pypi.python.org/pypi/docker-registry-driver-{{driver.name}}
[pypi-image]: https://badge.fury.io/py/docker-registry-driver-{{driver.name}}.svg

[travis-url]: http://travis-ci.org/{{driver.author.name}}/docker-registry-driver-{{driver.name}}
[travis-image]: https://secure.travis-ci.org/{{driver.author.name}}/docker-registry-driver-{{driver.name}}.png?branch=master

[coveralls-url]: https://coveralls.io/r/{{driver.author.name}}/docker-registry-{{driver.name}}
[coveralls-image]: https://coveralls.io/repos/{{driver.author.name}}/docker-registry-driver-{{driver.name}}/badge.png?branch=master
