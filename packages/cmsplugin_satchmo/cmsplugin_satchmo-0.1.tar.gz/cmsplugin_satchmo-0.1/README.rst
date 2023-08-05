=================
cmsplugin_satchmo
=================

cmsplugin_satchmo adds simple Satchmo e-commerce plugin to your djangoCMS
installation

Features:

- Unlimited, auto-discovered custom templates - you can change template
  of given product/category at anytime, use javascript or forms to adding to cart etc.

Contributions and comments are welcome using BitBucket at:
https://bitbucket.org/tomaasch/cmsplugin_satchmo

Please note that cmsplugin_satchmo requires:

* django-cms >= 2.2 https://github.com/divio/django-cms
* satchmo >= 0.9.3 https://satchmo.readthedocs.org/en/latest/ & https://bitbucket.org/chris1610/satchmo

Installation
============

#. `pip install cmsplugin_satchmo` or `easy_install cmsplugin_satchmo` (what you prefer)
#. Add `'cmsplugin_satchmo'` to `INSTALLED_APPS` (if necessary)
#. Run `syncdb` or `migrate cmsplugin_satchmo` if using South

Configuration
=============

#. Very simple templates are included with the project. Change or rewrite them.

Usage
=====

The easiest approach is to use a nice feature of cmsplugin_satchmo -
the template autodiscovery. In order to take advantage of it, add your custom
templates in the cmsplugin_satchmo subdirectory of any of template dirs scanned
by Django.

Embed as a typical plugin.

Bugs & Contribution
===================

Please use BitBucket to report bugs, feature requests and submit your code:
https://bitbucket.org/tomaasch/cmsplugin_satchmo

:date: 2014/05/28

