===========
Sundowner
===========

.. image:: https://travis-ci.org/kenners/sundowner.svg?branch=master
    :target: https://travis-ci.org/kenners/sundowner

Sundowner is a Python3 Flask application that provides an API to return JSON
objects containing Javascript timestamps of civil dawn, civil dusk, sunrise,
and sunset.

It also provides a simple web app that uses this API.

Sundowner uses `PyEphem <http://rhodesmill.org/pyephem/>`_ to calculate
astronomical parameters.

Sunrise and sunset times are calculated according to the United States Naval
Observatory specifications, whereby for dawn and dusk, atmospheric refraction is estimated by setting
observer pressure to zero and the horizon to 34 arcminutes below the normal
horizon.

Civil dawn and dusk are when the sun is 6º below the horizon.

Sundowner is licensed under the MIT License.

Dependencies
============

Sundowner has the following Python3 dependencies:

* Flask 0.10
* ephem 3.7
* itsdangerous 0.24
* Jinja2 2.7.2
* MarkupSafe 0.23
* Werkzeug 0.9.4
* python-dateutil 2.2

URL endpoints
=============

Sundowner exposes the following endpoint:

* ``/api/sun``

Parameters
----------

* ``<lat>`` and ``<lon>`` are simple decimals of latitude and longitude respectively,
  e.g. Rothera's location is expressed as -67.57 and -68.13
* ``<start>`` and ``<end>`` are start and end dates for the desired period, in ISO 8601
  format (as produced by Javascript's ``.toJSON()`` method)
* ``<output_type>`` is an optional parameter for the resulting datetimes,
  defaulting to ``iso`` for ISO 8601 format. Alternatively, use ``js``
  for Javascript timestamp, or ``dt`` for a human-readable datetime.

Output
======

The API returns a JSON object, as follows::

    {
      "days": [
        {
          "date": "2014-05-23",
          "events": {
            "civil_dawn": "2014-05-23T12:58:31.819853+00:00",
            "civil_dusk": "2014-05-23T19:59:14.923174+00:00",
            "sunrise": "2014-05-23T14:31:56.000752+00:00",
            "sunset": "2014-05-23T18:25:53.468033+00:00"
          }
        }
      ],
      "latlon": {
        "lat": "-67.57",
        "lon": "-68.13"
      }
    }

Acknowledgements
================

Sundowner uses the following components:

* Bootstrap v3.1.1 (http://getbootstrap.com)
  Licensed under the MIT License. (c) 2011-2014 Twitter, Inc
* HTML5 Shiv v3.7.0 (https://github.com/aFarkas/html5shiv)
  Licensed under the MIT License.
* jQuery v1.11.0 (http://jquery.org)
  Licensed under the MIT License. (c) 2005, 2014 jQuery Foundation, Inc.
* moment.js v2.6.0 (http://momentjs.com)
  Licensed under the MIT License. (c) 2011-2014 Tim Wood, Iskren Chernev,
  and Moment.js contributors
* Respond.js v1.4.2 (https://github.com/scottjehl/Respond)
  Licensed under the MIT License. (c) 2013 Scott Jehl
* bootstrap-datepicker v1.3.0 (http://eternicode.github.io/bootstrap-datepicker)
  Licensed under the Apache 2.0 License.

Full-text copies of the above licenses may be found at:

* http://opensource.org/licenses/MIT
* http://opensource.org/licenses/Apache-2.0
