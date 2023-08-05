Piston for Python 3.3+ and Django 1.6+
======================================

<https://bitbucket.org/userzimmermann/django-piston3>

* Compatible with __Python 2.7__
* Forked from <https://bitbucket.org/spookylukey/django-piston>
  ([diff](https://bitbucket.org/userzimmermann/django-piston3/branches/compare/master..spookylukey#diff))
* Based on <https://bitbucket.org/jespern/django-piston>
  ([diff](https://bitbucket.org/userzimmermann/django-piston3/branches/compare/master..jespern#diff))
* Merged with <https://bitbucket.org/j00bar/django-piston>
  ([diff](https://bitbucket.org/userzimmermann/django-piston3/branches/compare/master..j00bar#diff))


Usage
-----

* Import `piston3` instead of `piston`
* Original documentation:
  <https://bitbucket.org/jespern/django-piston/wiki/Home>

### Issues

* Creation of `request.PUT` and `request.FILES` on __PUT__ requests,
  handled by `piston3.utils.coerce_put_post`, doesn't work properly,
  `Issue36RegressionTests` __fail__
* All other tests __pass__


Setup
-----

### Requirements

* [`six`](https://bitbucket.org/gutworth/six)
* [`python-mimeparse`](https://github.com/dbtsai/python-mimeparse)
* [`django >= 1.6`](http://www.djangoproject.com)

### Installation

    python setup.py install

Or with [pip](http://www.pip-installer.org):

    pip install .

Or from [PyPI](https://pypi.python.org/pypi/django-piston3):

    pip install django-piston3
