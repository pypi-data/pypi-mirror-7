Introduction
============
This product add a patch to deleteObjectsByPaths method to avoid acquisition delete problem.

To see more details, go to Plone ticket `#13603 <https://dev.plone.org/ticket/13603>`_

Plone versions affected
=======================

All versions < 4.3.3

This bug is already fixed in Plone 4.3.3 (Products.CMFPlone)

Plone 4.0 Buildout Installation
===============================

To install rer.fix13603, add the following code to your buildout.cfg::

    [buildout]

    ...

    [instance]
    ...
    eggs =
        ...
        rer.fix13603

    ...

This product doesn't need to be installed because only apply a monkeypatch.

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
