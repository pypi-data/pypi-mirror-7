piprot
======

How rotten are your requirements?

tl;dr: piprot allows you to check the requirements defined in your
requirements files for freshness.

.. figure:: http://i.imgur.com/kewPaFa.gif
   :alt: piprot Demo

   piprot Demo
Installation
~~~~~~~~~~~~

piprot can be installed via PyPI

::

    pip install -U piprot

Basic Usage
~~~~~~~~~~~

Run piprot and provide a requirements file (if it's not called
requirements.txt):

::

    > piprot base_requirements.txt
    requests (2.3.0) is up to date
    six (1.6.1) is 107 days out of date. Latest is 1.7.3
    piprot (0.6.0) is up to date
    doge (3.4.0) is 129 days out of date. Latest is 3.5.0
    Your requirements are 236 days out of date

If your requirements file is named "requirements.txt", you don't need to
provide it.

The --verbatim argument will output your complete requirements file,
with some comments about the out of date nature of your packages.

::

    > piprot --verbatim
    # Requirements for Piprot
    # This actually doubles as a test file

    requests==2.3.0
    six==1.6.1 # Latest 1.7.3

    piprot==0.6.0
    # notarequirement==0.1.1

    doge==3.4.0 # Latest 3.5.0
    # Generated with piprot 0.7.0
    # Your requirements are 236 days out of date

Using --outdated will show only the out of date requirements, pretty
much the same as running ``pip list -o``, except on a requirements file.

::

    > piprot --outdated
    six (1.6.1) is 107 days out of date. Latest is 1.7.3
    doge (3.4.0) is 129 days out of date. Latest is 3.5.0
    Your requirements are 236 days out of date

Yep, you can use stdin as well if you really want to, but there are
better tools for working with packages installed in your environment.

::

    pip freeze | piprot

And what I like to do is use --verbatim and push it back out into
another file.

::

    piprot --verbatim > reqs.txt

Working with your environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

piprot is designed around working with requirements defined in a
requirements file. Check out
`pip-tools <https://github.com/nvie/pip-tools>`__ if you're looking for
something similar that's designed for use against the packages that you
actually have installed.

Notifications
~~~~~~~~~~~~~

Since version 0.7.0 piprot has had support for uploading your
requirements to `piprot.io <https://piprot.io>`__ to receive weekly
notifications about packages that have been updated. You can upload your
requirements using a command like this:

::

    piprot --notify=brenton@piprot.io requirements.txt

This service was created by @sesh (the creator of this tool, me!) and
will at some point in the future require a small fee for ongoing
notifications.

Tests
~~~~~

To run the test suite, execute ``python -m unittest discover``, within
the project directory.

Please ensure that the (limited) tests are all passing before making a
pull request. Feel free to add more.
