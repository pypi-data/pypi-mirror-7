# Flask-Statics-Helper

Provides Bootstrap3 and other static resources in a modular fashion.

The main purpose of this extension is to "modularize" static resources (css and js files) on a per-template basis. In a
large Flask application, all views/templates don't use the same static resource such as d3js. If only one view uses d3js
out of five or more, there is no reason to have the d3js `<script />` tag included in all views.

This extension also provides a base template to be extended by your Flask application's templates for Bootstrap3 (like
other Bootstrap3 extensions such as [this](https://github.com/mbr/flask-bootstrap) or
[this](https://github.com/ryanolson/flask-bootstrap3)).

[![Build Status](https://travis-ci.org/Robpol86/Flask-Statics-Helper.svg?branch=master)]
(https://travis-ci.org/Robpol86/Flask-Statics-Helper)
[![Latest Version](https://pypip.in/version/Flask-Statics-Helper/badge.png)]
(https://pypi.python.org/pypi/Flask-Statics-Helper/)
[![Downloads](https://pypip.in/download/Flask-Statics-Helper/badge.png)]
(https://pypi.python.org/pypi/Flask-Statics-Helper/)
[![Download format](https://pypip.in/format/Flask-Statics-Helper/badge.png)]
(https://pypi.python.org/pypi/Flask-Statics-Helper/)
[![License](https://pypip.in/license/Flask-Statics-Helper/badge.png)]
(https://pypi.python.org/pypi/Flask-Statics-Helper/)

## Supported Platforms

* OSX and Linux.
* Python 2.6, 2.7, 3.3, 3.4
* [Flask](http://flask.pocoo.org/) 0.10.1

## Quickstart

Install:
```bash
pip install Flask-Statics-Helper
```

Enable:
```python
# example.py
from flask import Flask
from flask.ext.statics import Statics

app = Flask(__name__)
Statics(app)
```

Use with Bootstrap3 (automatically enables jQuery):
```html+django
{% extends 'flask_statics_helper/bootstrap.html' %}
{% set STATICS_ENABLE_RESOURCE_CSSHAKE = True %}
{% block title %}My Application{% endblock %}

{% block navbar %}
    <div class="navbar navbar-inverse navbar-static-top" role="navigation">
        <div class="container">
            <div class="navbar-header"> <!-- navbar-header -->
                <button type="button" class="navbar-toggle" data-toggle="collapse"
                        data-target=".navbar-collapse">
                    <span class="sr-only">Toggle navigation</span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                </button>
                <a class="navbar-brand" href="/">My Application</a>
            </div> <!-- /navbar-header -->
            <div class="collapse navbar-collapse"> <!-- navbar-collapse -->
                <ul class="nav navbar-nav">
                    <li><a href="/">Home</a></li>
                </ul>
            </div> <!-- /navbar-collapse -->
        </div>
    </div>
{% endblock %}

{% block container %}
    <div class="jumbotron">
        <h2 class="shake shake-constantly">Hello World.</h2>
    </div>
{% endblock %}
```

## Available Resources

* [Bootstrap](http://getbootstrap.com/) 3.2.0
* [jQuery](http://jquery.com/) 2.1.1
* [Font Awesome](http://fortawesome.github.io/Font-Awesome/) 4.1.0
* [WHHG Font](http://www.webhostinghub.com/glyphs/) (cloned July 9, 2014)
* [Bootstrap Growl](https://github.com/mouse0270/bootstrap-growl) 2.0.0
* [Bootstrap X-Editable](http://vitalets.github.io/x-editable/) 1.5.1
* [Bootstrap 3 Typeahead](https://github.com/bassjobsen/Bootstrap-3-Typeahead) 3.0.3
* [CSShake](https://github.com/elrumordelaluz/csshake) (cloned July 9, 2014)
* [Data Tables](http://datatables.net/) 1.10.0
* [Angular JS](https://angularjs.org/) 1.3.0 beta 14
* [D3](http://d3js.org/) 3.4.9

## Configuration

The only `app.config` specific setting is `STATICS_MINIFY`. Everything else may be set to True either in individual
templates (so that css/js is included only for that template) or you may set it to True in the `app.config` if you want
the resource enabled for all templates for some reason or another.

The following config settings are searched for in the Flask application's configuration dictionary:
* `STATICS_MINIFY` -- Have minified resources selected instead of uncompressed resources.
* `STATICS_ENABLE_RESOURCE_ANGULARJS` -- include resource in all templates.
* `STATICS_ENABLE_RESOURCE_BOOTSTRAP` -- include resource in all templates.
* `STATICS_ENABLE_RESOURCE_BOOTSTRAP_EDITABLE` --  include resource in all templates.
* `STATICS_ENABLE_RESOURCE_BOOTSTRAP_GROWL` --  include resource in all templates.
* `STATICS_ENABLE_RESOURCE_BOOTSTRAP_TYPEAHEAD` --  include resource in all templates.
* `STATICS_ENABLE_RESOURCE_CSSHAKE` --  include resource in all templates.
* `STATICS_ENABLE_RESOURCE_D3` --  include resource in all templates.
* `STATICS_ENABLE_RESOURCE_DATATABLES` --  include resource in all templates.
* `STATICS_ENABLE_RESOURCE_FONT_AWESOME` --  include resource in all templates.
* `STATICS_ENABLE_RESOURCE_JQUERY` --  include resource in all templates.
* `STATICS_ENABLE_RESOURCE_WHHG_FONT` --  include resource in all templates.
* `STATICS_ENABLE_RESOURCE_ANGULARJS_ANIMATE` --  include resource in all templates.
* `STATICS_ENABLE_RESOURCE_ANGULARJS_COOKIES` --  include resource in all templates.
* `STATICS_ENABLE_RESOURCE_ANGULARJS_CSP` --  include resource in all templates.
* `STATICS_ENABLE_RESOURCE_ANGULARJS_LOADER` --  include resource in all templates.
* `STATICS_ENABLE_RESOURCE_ANGULARJS_MESSAGES` --  include resource in all templates.
* `STATICS_ENABLE_RESOURCE_ANGULARJS_MOCKS` --  include resource in all templates.
* `STATICS_ENABLE_RESOURCE_ANGULARJS_RESOURCE` --  include resource in all templates.
* `STATICS_ENABLE_RESOURCE_ANGULARJS_ROUTE` --  include resource in all templates.
* `STATICS_ENABLE_RESOURCE_ANGULARJS_SANITIZE` --  include resource in all templates.
* `STATICS_ENABLE_RESOURCE_ANGULARJS_SCENARIO` --  include resource in all templates.
* `STATICS_ENABLE_RESOURCE_ANGULARJS_TOUCH` --  include resource in all templates.

## Changelog

#### 0.1.1

* Added Python 2.6 and 3.x support.

#### 0.1.0

* Initial release.
