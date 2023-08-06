.. contents::

Introduction
============

A **booking product for Plone** to reserve time slots throughout the week.


Customizations
==============

This product is an extension that customizes `rg.prenotazioni`__

__ https://pypi.python.org/pypi/rg.prenotazioni


Custom mail action
------------------

The product overrides the mail action defined by
`collective.contentrules.mailfromfield`__, providing additional markers
dedicate to the booking product:

- `${gate}`
- `${date}`
- `${time}`
- `${type}`

__ https://pypi.python.org/pypi/collective.contentrules.mailfromfield


Custom event log
----------------

The product registers, optionally, some events to an external logfile:

- booking creation
- booking workflow state modification
- booking date/time modification

In order to track modification the product adds the booking content type
to the reposository tool.

The custom event log has to be enabled adding to the instance part
of your buildout this snippet::

  zope-conf-additional +=
    <product-config pd.prenotazioni>
        logfile ${buildout:directory}/var/log/prenotazioni.log
    </product-config>


Customized Searchable text
--------------------------

Searchable text for booking objects is customized in order to add
the modification comments to the index.

The product removes from the booking searchable text those fields:

- gate
- subject
- location


Popup with tooltipster
----------------------

The product adds to the agenda some popups using the library `tooltipster`__

__ http://iamceege.github.io/tooltipster/


Credits
=======

Developed with the support of `Comune di Padova`__;
Comune di Padova supports the `PloneGov initiative`__.

.. image:: http://prenotazioni.comune.padova.it/++resource++pd.plonetheme.images/title.png
   :alt: Comune di Padova's logo

__ http://www.padovanet.it/
__ http://www.plonegov.it/


Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.it/redturtle_banner.png
   :alt: RedTurtle Technology Site
      :target: http://www.redturtle.it/


