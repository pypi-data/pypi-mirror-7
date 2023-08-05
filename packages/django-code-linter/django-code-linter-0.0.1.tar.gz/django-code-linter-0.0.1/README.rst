==================
django-code-linter
==================


Features
========

* simple validation of model imports in migrations

Usage
=====

.. code-block:: bash

   pip install django-code-linter
   djinter ./your-project

``djinter`` script also exits with non-zero exit-code when something is wrong so you can use in in your
Makefile:

.. code-block:: Makefile

   test:
   	manage.py test
   	djinter ./your-project