Introduction
============

A Plone customization for the "*Contact the author*" form.

Normally in Plone only authenticated member can send internal messages to the author. This product open
the form also to anonymous users.

When anonymous try to contact an author, they must provide also an email address and a captcha protection
value.

.. image:: http://keul.it/images/plone/collective.contactauthor-0.1.0.png
   :alt: How the form looks like

Please note that access to the ``author`` page is still guarded by the Plone setting
"*Allow anyone to view 'about' information*" in the "*Security settings*" control panel.

You can still edit the contact author configuration from the new "*Contact author settings*" to change
this behavior. You can restore Plone default (where users must be authenticated) or freely enable it
to all anoymous users (this can be dangerous... this option is only provided for some intranet purpose).

Form protection
---------------

The captcha protection is given by the `collective.recaptcha`__ product.

__ http://pypi.python.org/pypi/collective.recaptcha

Security
========

Keep in mind that, even behind a robot/bot protection, this product open your site to anonymous message from
the Web. It's mainly targeted to intranet environment.

The given anonymous email can be unexistent (or the someone else ones).

Dependencies
============

This product has been tested on Plone 4.3.

Credits
=======

Developed with the support of `S. Anna Hospital, Ferrara`__; S. Anna Hospital supports the
`PloneGov initiative`__.

__ http://www.ospfe.it/
__ http://www.plonegov.it/

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.net/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.net/

