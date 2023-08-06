|build|

======================
validate-email-address
======================

`validate-email-address` is a package for Python that check if an email is valid, properly formatted and really exists.



INSTALLATION
============

First, you must do::

    pip install validate-email-address


Extra
-----

For check the domain mx and verify email exits you must have the `pyDNS` package installed::

    pip install pyDNS


USAGE
=====

Basic usage::

    >>> from validate_email_address import validate_email
    >>> validate_email('example@example.com')
    True


Checking domain has SMTP Server
-------------------------------

Check if the host has SMTP Server::

    >>> from validate_email_address import validate_email
    >>> validate_email('example@sharklasers.com', check_mx=True)
    True


Verify email exists
-------------------

Check if the host has SMTP Server and the email really exists::

    >>> from validate_email_address import validate_email
    >>> validate_email('example@sharklasers.com', verify=True)
    True


.. |build| image:: https://travis-ci.org/heropunch/validate-email-address.svg
   :target: https://travis-ci.org/heropunch/validate-email-address