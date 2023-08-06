|PyPI badge| |Installs badge| |License badge| |Wheel badge|

Django Inventory
----------------

Free Open Source Inventory and Fixed Assets Control System

.. image:: http://img814.imageshack.us/img814/5088/screenshot1fz.png
.. image:: http://img443.imageshack.us/img443/1486/screenshot2wu.png

`Translations`_


Features
--------

* Object oriented approach to asset and inventory management.
* CSV import utility.
* Per asset or per item type photos and information.
* Match suppliers to item types.
* Site wide search capability.
* User defined states (broken, in repairs, etc) for assets.
* An item can be defined as a supply to another item.
* Assign assets to one or more individuals.
* User photos.
* Group assets, inventories or user per locations.
* Purchase request and purchase orders.


License
-------

This project is open sourced under `Apache 2.0 License`_.


Installation
------------

To install **Django Inventory**, simply do:

.. code-block:: bash

    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install django-inventory==1.0rc1
    $ django-inventory.py initialsetup
    $ django-inventory.py runserver

Point your browser to 127.0.0.1:8000 and use the automatically created admin
account.

Contribute
----------

- Check for open issues or open a fresh issue to start a discussion around a feature idea or a bug.
- Fork `the repository`_ on GitHub to start making your changes to the **master** branch (or branch off of it).
- Write a test which shows that the bug was fixed or that the feature works as expected.
- Make sure to add yourself to the `contributors file`_.
- Send a pull request


Author
------

Roberto Rosario - **Twitter** http://twitter.com/siloraptor **E-mail** roberto.rosario.gonzalez at gmail


.. _Translations: https://www.transifex.com/projects/p/django-inventory/
.. _Apache 2.0 License: https://www.apache.org/licenses/LICENSE-2.0.txt
.. _`the repository`: http://github.com/rosarior/django-inventory
.. _`contributors file`: https://github.com/rosarior/django-inventory/blob/master/docs/contributors.rst
.. |Installs badge| image:: http://img.shields.io/pypi/dm/django-inventory.svg?style=flat
   :target: https://crate.io/packages/django-inventory/
.. |PyPI badge| image:: http://img.shields.io/pypi/v/django-inventory.svg?style=flat
   :target: http://badge.fury.io/py/django-inventory
.. |Wheel badge| image:: http://img.shields.io/badge/wheel-yes-green.svg?style=flat
.. |License badge| image:: http://img.shields.io/badge/license-Apache%202.0-green.svg?style=flat

