Django docopt command
=====================

|Build Status|

Django-docopt-command allows you to write
`Django <https://www.djangoproject.com>`__
`manage.py <https://docs.djangoproject.com/en/dev/howto/custom-management-commands/>`__
commands using the `docopt <http://www.docopt.org>`__ library. This
means that you can define commands using usage strings.

References:

-  `Django <https://www.djangoproject.com>`__: The Web framework for
   perfectionists with deadlines
-  `The docopt library <http://www.docopt.org>`__: Command-line
   interface description language
-  `Writing custom django-admin
   commands <https://docs.djangoproject.com/en/dev/howto/custom-management-commands/>`__

::

    class Command(DocOptCommand):
        # This usage string defines the command options:
        docs = "Usage: command <option1> <option2> [--flag1]"

        def handle_docopt(self, arguments):
            # arguments contains a dictionary with the options
            pass

Django-docopt-command is tested with Django 1.4-1.7 and Python 2.6, 2.7, 3.3 and 3.4 and is hosted on
`github <https://github.com/mbraak/django-docopt-command>`__.

Example
~~~~~~~

See the *testproject/docopt\_example* in the django-docopt-command
github repository.

Usage
-----

Install django-docopt-command.

::

    pip install django-docopt-command

**Step 1 - management command**

Write a Django custom management command, as described in `Writing
custom django-admin
commands <https://docs.djangoproject.com/en/dev/howto/custom-management-commands/>`__.

**Step 2 - inherit from DocOptCommand**

::

    class Command(DocOptCommand):
        pass

**Step 3 - add a docs string**

::

    class Command(DocOptCommand):
        docs = "Usage: command <option1> <option2> [--flag1]"

**Step 4 - override handle\_docopt**

::

    class Command(DocOptCommand):
        docs = "Usage: command <option1> <option2> [--flag1]"

        def handle_docopt(self, arguments):
            pass

License
-------

Django-docopt-command is licensed under the Apache 2.0 License.

.. |Build Status| image:: https://travis-ci.org/mbraak/django-docopt-command.png?branch=master
   :target: https://travis-ci.org/mbraak/django-docopt-command
