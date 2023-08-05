Change default Plone behavior in **locking documents** management: add a new (specific) permission
instead of relying onto the modify permission.

Introduction
============

Plone has a native locking protection given bt the `plone.locking`__ module but, as said in the
documentation, users able to modify a document can always steal the lock.

__ https://github.com/plone/plone.locking

How this works
==============

This add-on adds a new different permission for locking: ``collective.filteredlocking: Can unlock objects``.

Users without this permission will be not able to unlock the document until it's released by the owner or
lock expires.

Credits
=======

Developed with the support of `Regione Emilia Romagna`__;
Regione Emilia Romagna supports the `PloneGov initiative`__.

__ http://www.regione.emilia-romagna.it/
__ http://www.plonegov.it/

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.it/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/
