Address auto completion for australia
=====================================

.. image:: https://travis-ci.org/openlabs/trytond-address-autocomplete-au.svg?branch=develop
    :target: https://travis-ci.org/openlabs/trytond-address-autocomplete-au


.. image:: https://coveralls.io/repos/openlabs/trytond-address-autocomplete-au/badge.png
    :target: https://coveralls.io/r/openlabs/trytond-address-autocomplete-au


This tryton module enhances the user experience in filling in addresses.
The module tries to autocomplete addresses from the partially filled in
street information or pin (zip) codes.

.. note::

   The autocompletion requires Australia Post web service.

Installation
------------

The module can be installed from PyPI::

    pip install openlabs_address_autocomplete_au

or from the sources::

    git clone git@github.com:openlabs/trytond-address-autocomplete-au.git
    cd trytond-address-autocomplete-au
    python setup.py install

Configuration
-------------

After installating the module, the API key needs to be set in the `Party
configuration`. The API key can be obtained from `Australia Post Website
<https://auspost.com.au/forms/pacpcs-registration.html>`_.

.. note::

    If the API key is not set the autocompletion fails silently with a log
    warning.

Authors and Contributors
------------------------

This module was built at `Openlabs <http://www.openlabs.co.in>`_. 

Professional Support
--------------------

This module is professionally supported by `Openlabs <http://www.openlabs.co.in>`_.
If you are looking for on-site teaching or consulting support, contact our
`sales <mailto:sales@openlabs.co.in>`_ and `support
<mailto:support@openlabs.co.in>`_ teams.
