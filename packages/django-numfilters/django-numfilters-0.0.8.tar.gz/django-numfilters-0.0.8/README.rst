django-numfilters
=================

.. image:: https://travis-ci.org/amatellanes/django-numfilters.svg?branch=master
    :target: https://travis-ci.org/amatellanes/django-numfilters
    
**django-numfilters** is a collection of template filters for Django who provides access to several basic mathematical functions.

Download
--------

To install it by using `pip`_: ::

    $ pip install django-numfilters

or by using `easy_install`_: ::
    
    $ easy_install django-numfilters
    
You can also pot for installing it from source: ::
    
    $ git clone git@github.com:amatellanes/django-numfilters.git
    $ cd django-numfilters
    $ python setup.py install

.. _pip: https://pypi.python.org/pypi/pip
.. _easy_install: https://pypi.python.org/pypi/setuptools

Installation
------------

To enable **django-numfilters** in your Django project, you need to add `django_numfilters` to `INSTALLED_APPS`: ::

    INSTALLED_APPS = (
        ...
        'django_numfilters',
        ...
    )

Usage
-----

This section provides a summary of **django-numfilters** features.

Firstly, you need make filters available to your templates using `{% load numfilters %}` tag. After this, you can use 
next tags:

`abs`
  Returns the absolute value of `a`, for `a` number.
  
`add`
  This filter is provided by `Django`_.

`sub`
  Returns `a - b`, for `a` and `b` numbers.
  
`mul`
  Returns `a * b`, for `a` and `b` numbers.
  
`div`
  Returns `a / b`, for `a` and `b` numbers (*classic* division).
  
`mod`
  Returns `a % b`, for `a` and `b` numbers.
  
`floordiv`
  Returns `a // b`, for `a` and `b` numbers.
  
`pow`
  Returns `a ** b`, for `a` and `b` numbers. 
  
`sqrt`
  Return the square root of `a`, for `a` number.
  
.. _Django: https://docs.djangoproject.com/en/dev/ref/templates/builtins/#add
  
**Example**

.. sourcecode:: html

    {% load numfilters %}
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Example django-numfilters</title>
    </head>
    <body>
    <ul>
    
        <li>abs(-41) = {{ -41|abs }}</li>
    
        <li>23 - 7 = {{ 23|sub:7 }}</li>
    
        <li>25 * 2 = {{ 25|mul:2 }}</li>
    
        <li>32 / 4 = {{ 32|div:4 }}</li>
    
        {% with a=15 b=3 %}
            <li>15 % 3 = {{ a|mod:b }}</li>
        {% endwith %}
    
        {% with a=5 b=2 %}
            <li>5 // 2 = {{ 5|floordiv:2 }}</li>
        {% endwith %}
    
        <li>pow(5, 2) = {{ 5|pow:2 }}</li>
    
        {% with a=6 %}
            <li>sqrt(64) = {{ 64|sqrt }}</li>
        {% endwith %}
    
    </ul>
    </body>
    </html>


Changelog
---------

Release 0.1.0 (Unreleased)

- Initial release.

License
-------

`MIT License <http://www.tldrlegal.com/license/mit-license>`_, see LICENSE file.