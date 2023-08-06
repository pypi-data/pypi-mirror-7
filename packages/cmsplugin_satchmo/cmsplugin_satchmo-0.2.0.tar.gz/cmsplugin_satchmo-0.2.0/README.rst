=================
cmsplugin_satchmo
=================

cmsplugin_satchmo adds simple Satchmo e-commerce plugin to your djangoCMS installation

Features:

- Link teaser to any Satchmo product or category
- Create box with Satchmo product listing (recent, bestsellers, featured)
- Create box with Satchmo categories listing
- Unlimited, auto-discovered custom templates - you can change template
  of given product/category at anytime, use javascript or forms to adding to cart etc.
- Multi site support - you can link product from one Satchmo project into other
  Django CMS instalation (they must run on one database connection, of course)

Contributions and comments are welcome using BitBucket at:
https://bitbucket.org/tomaasch/cmsplugin_satchmo

Please note that cmsplugin_satchmo requires:

* django-cms >= 2.4 https://github.com/divio/django-cms
* satchmo >= 0.9.3 https://satchmo.readthedocs.org/en/latest/ & https://bitbucket.org/chris1610/satchmo
(maybe it works with earlier software version too but it's not tested)

Installation
============

#. 'pip install cmsplugin_satchmo' or 'easy_install cmsplugin_satchmo' (what you prefer)
#. Add 'product', 'tax', 'l10n', 'satchmo_store.contact', 'livesettings', 'keyedcache',
   'satchmo_utils' and 'app_plugins' to INSTALLED_APPS (if missing there)
#. Add 'cmsplugin_satchmo' to INSTALLED_APPS
#. Run 'manage.py syncdb' or 'manage.py migrate cmsplugin_satchmo' if using South

Configuration
=============

#. Very simple templates are included with the project. Change or rewrite them.
#. Go to the section 'CMS plugin Satchmo Settings' in admin interface and add record for each your satchmo site
   (need to define variables like 'SHOP_BASE', 'PRODUCT_SLUG' and 'CATEGORY_SLUG' for every site)


Usage
=====

The easiest approach is to use a nice feature of cmsplugin_satchmo -
the template autodiscovery. In order to take advantage of it, add your custom
templates in the cmsplugin_satchmo subdirectory of any of template dirs scanned
by Django.

Embed as a typical Django CMS plugin.

Bugs & Contribution
===================

Please use BitBucket to report bugs, feature requests and submit your code:
https://bitbucket.org/tomaasch/cmsplugin_satchmo

:date: 2014/05/28

