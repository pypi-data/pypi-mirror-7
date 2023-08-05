A new way to controls how Plone **marks external links** or **open them in popup** windows.

.. contents::

Introduction
============

Plone has already two feature named "*Mark external links*" and "*External links open in new window*" that
make the CMS to change apprearence of external link or open them in popup windows.

However native Plone features are on-or-off: you can't choose the criteria used for mark links or choose which
ones will be opened in a new windows.

How it works
============

After installation go to the "*Externalize links settings*" in the control panel and configure your preferences.

.. image:: http://keul.it/images/plone/collective.externalizelink/collective.externalizelink-0.1.0-01.png
   :alt: Control panel

*Links selectors*
    Use this section to enter a set of jQuery selector that match your links.
*Mark processed links*
    For every processed link you can also provide additional attributes for example a new CSS class.

Plus, the *title* attribute of every link will be enhanced with a text that warn the user of the "popup"
nature ("*It will open in a new window*"). 

Motivations behind the product
==============================

Apart the effective usefulness of the product, this has been mainly written as example application for
the use of `collective.jsconfiguration`__.

__ https://github.com/keul/collective.jsconfiguration

