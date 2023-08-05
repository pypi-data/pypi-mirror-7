PokitDok Platform API Client for Python
=======================================

Installation
------------

Install from PyPI_ using pip_

.. code-block:: bash

    $ pip install pokitdok


Resources
---------

Report issues_ on GitHub


Quick start
-----------

.. code-block:: python

    import pokitdok

    pd = pokitdok.api.connect('<your client id>', '<your client secret>')

    #submit an eligibility request
    eligibility_response = pd.eligibility({
        "trading_partner_id": "MOCKPAYER",
        "member_id": "W00000000000",
        "provider_id": "1467560003",
        "provider_name": "AYA-AY",
        "provider_first_name": "JEROME",
        "provider_type": "Person",
        "member_name": "JANE DOE",
        "member_birth_date": "1970-01-01",
        "service_types": ["Health Benefit Plan Coverage"]
    })

    #retrieve provider information by NPI
    pd.providers(npi='1467560003')

    #search providers by name (individuals)
    pd.providers(first_name='Jerome', last_name='Aya-Ay')

    #search providers by name (organizations)
    pd.providers(organization_name='Qliance')

    #search providers by location and/or specialty
    pd.providers(zipcode='29307', radius='10mi')
    pd.providers(zipcode='29307', radius='10mi', specialty='RHEUMATOLOGY')

    #Submit X12 files directly for processing on the platform
    pd.files('MOCKPAYER', '/x12_files/eligibility_requests_batch_20.270')

    #Check on pending platform activities

    #check on a specific activity
    pd.activities(activity_id='5362b5a064da150ef6f2526c')

    #check on a batch of activities
    pd.activities(parent_id='537cd4b240b35755f5128d5c')

    #retrieve an index of activities
    pd.activities()



See the documentation_ for detailed information on all of the PokitDok Platform APIs

Supported Python Versions
-------------------------

This library aims to support and is tested against these Python versions:

* 2.6.9
* 2.7.6
* 3.4.0
* PyPy

You may have luck with other interpreters - let us know how it goes.

License
-------

Copyright (c) 2014 PokitDok, Inc.  See LICENSE_ for details.

.. _documentation: https://platform.pokitdok.com
.. _issues: https://github.com/pokitdok/pokitdok-python/issues
.. _PyPI: https://pypi.python.org/pypi
.. _pip: https://pypi.python.org/pypi/pip
.. _LICENSE: LICENSE.txt

