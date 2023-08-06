This product will replace the basic Plone feature for **adding analytics JavaScript to your site**
with an advanced version.

.. contents:: **Table of contents**

Introduction
============

New features added:

* add possibility to add specific JavaScript when the user is **inside error page**
  (useful for special code when on the "*Page not found*")
* add possibility to **customize code for a site area** or a single content
* not display JavaScript code for specific area of the site
* choose to put you snippets in the page header or footer)

How to use it
=============

When installed, the basic Plone feature for handling JavaScript for statistics is hidden from the standard
"*Site settings*" (in facts, it's moved to a new configuration panel called "*Analytics settings*") and
new options are now available.

JavaScript for web statistics support 
-------------------------------------

.. image:: https://blog.redturtle.it/pypi-images/collective.analyticspanel/collective.analyticspanel-0.4.0-01.png
   :alt: Basic feature

Nothing new there: this is simply the basic Plone feature about JavaScript inclusion, just moved in this
separate panel (and you can put it in the header of the page).
This is always the default code included when other options don't match.

JavaScript to be included when an error message is get 
------------------------------------------------------

.. image:: http://blog.redturtle.it/pypi-images/collective.analyticspanel/collective.analyticspanel-0.4.0-02.png
   :alt: Code for error page

When this product is installed you can control JavaScript code based on error messages (ignoring the default one).
The main motivation is to use this for the ``NotFound`` (HTTP 404) error.

However this feature is still generic... you could probably use it for other error code (like ``ValueError``)
if this make any sense for you!

JavaScript to be included inside specific site's paths 
------------------------------------------------------

.. image:: http://blog.redturtle.it/pypi-images/collective.analyticspanel/collective.analyticspanel-0.4.0-03.png
   :alt: Code for specific site's path

You can use this section for putting a list of absolute site subsection you want to control, adding a specific
JavaScript section and ignoring the default one.

When more than a provided path match the current URL, the most specific ones is used.

This kind of rule has a policy selection.

.. image:: http://blog.redturtle.it/pypi-images/collective.analyticspanel/collective.analyticspanel-0.3.0-04.png
   :align: right
   :alt: Policy selection

* The default one ("*to the whole subtree*") is for applying the rule to the whole subtree.
* Using "*only to the context*" you can choose to apply the analytics code only to the content and not
  to sub-contents inside it.
* Using "*to the context and non-folderish children*" you are applying the analytics code only to the content,
  and to all sub-contents inside it that are not folders.

This last policy seems a little complex, but there are analytics tools (at least: `Piwik`__) where this can
be useful to define custom reports for sections of the site.

__ http://piwik.org/

As the concept of "folder" in Plone can change with different add-ons installed, this last policy take care
of using as "folder" what is defined in the "*Folderish types*" configuration option.

.. image:: http://blog.redturtle.it/pypi-images/collective.analyticspanel/collective.analyticspanel-0.3.0-05.png
   :alt: Folderish types selection panel

The Plone native "Folder" type is selected by default.

Hiding
------

You can also use this product for hiding analytics code from specific site areas or error pages, leaving a default
one for the rest of the site.

Just configure options with empty code!

JavaScript in the header or footer of the page?
===============================================

Historically Plone put analytics code in the page footer; this is an old way to go and modern analytics
software suggest to put you code before the ``body`` tag.
However old analytics software that can block the page rendering are better to be kept at the end of the page.

For this reason this product will let you add analytics on both header or footer of the page at your choice.

As you seen this option is available everywhere, for every feature added, just note that analytics in the header
or footer are treat separately.

Dependencies
============

This product has been tested on:

* Plone 3.3 (read below)
* Plone 4.2
* Plone 4.3

It's based on `plone.app.registry`__ that it not part of Plone on 3.3 version. You need to be sure that a compatible
version is used (in my experience: use `plone.app.registry 1.0b1`__ and `plone.registry 1.0`__).

__ http://pypi.python.org/pypi/plone.app.registry
__ http://pypi.python.org/pypi/plone.app.registry/1.0b1
__ http://pypi.python.org/pypi/plone.registry/1.0

Credits
=======
  
Developed with the support of:

* `Regione Emilia Romagna`__

* `Provincia di Ferrara`__

  .. image:: http://www.provincia.fe.it/Distribuzione/logo_provincia.png
     :alt: Provincia di Ferrara - logo

All of them supports the `PloneGov initiative`__.

__ http://www.regione.emilia-romagna.it/
__ http://www.provincia.fe.it/
__ http://www.plonegov.it/

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.it/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/
