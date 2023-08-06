================
django-email-log
================

.. image:: https://travis-ci.org/treyhunner/django-email-log.png?branch=master
   :target: https://travis-ci.org/treyhunner/django-email-log
   :alt: Test Status

.. image:: https://coveralls.io/repos/treyhunner/django-email-log/badge.png?branch=master
   :target: https://coveralls.io/r/treyhunner/django-email-log
   :alt: Coverage Status

.. image:: https://pypip.in/v/django-email-log/badge.png
   :target: https://crate.io/packages/django-email-log
   :alt: Latest Version

.. image:: https://pypip.in/d/django-email-log/badge.png
   :target: https://crate.io/packages/django-email-log
   :alt: Download Count

.. image:: https://requires.io/github/treyhunner/django-email-log/requirements.png?branch=master
   :target: https://requires.io/github/treyhunner/django-email-log/requirements
   :alt: Requirements Status/

Django email backend that logs all sent emails.

This app requires Django 1.4.13 or greater and Python 2.6+ or Python3.3+.

Getting Help
------------

Documentation for django-email-log is available at https://django-email-log.readthedocs.org/

This app is available on `PyPI`_.

Submit issues on Github: https://github.com/treyhunner/django-email-log/issues

Pull requests are welcome.  Read the CONTRIBUTING file for tips on submitting
a pull request.

.. _PyPI: https://pypi.python.org/pypi/django-email-log/


Related Projects
----------------

Thanks to the following related projects for inspiration:

- `django-mailer`_
- `django-post_office`_
- `django-celery-email`_
- Email logger mentioned in this `StackOverflow answer`_

.. _django-mailer: https://github.com/pinax/django-mailer
.. _django-celery-email: https://github.com/pmclanahan/django-celery-email
.. _django-post_office: https://github.com/ui/django-post_office
.. _stackoverflow answer: http://stackoverflow.com/a/7553759/98187


CHANGES
=======

0.2.0 (2014-08-03)
------------------

- Added Django 1.6 and Django 1.7 support.
- Added German and Brazilian Portuguese translations (#3 and #9).  Thanks
  Jannis and Rodrigo Deodoro.
- Fixed email log app name on admin website.
- Output email body in admin interface with linebreaks shown correctly (#6).
  Thanks Keryn Knight.

0.1.0 (2013-05-02)
------------------

Initial release.


