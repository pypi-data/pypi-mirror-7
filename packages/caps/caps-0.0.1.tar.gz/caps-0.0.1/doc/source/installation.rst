
.. _install_guid:

==================
Installing `CAPS`
==================

This tutorial will walk you through the process of intalling CAPS...

  * :ref:`Install an official release <install_release>`. This
    is the best approach for users who want a stable version.

  * :ref:`Install the latest development version
    <install_development>`. This is best for users who want to contribute
    to the project.


.. _install_release:

Installing a stable version
==============================

Install the python package with *pip*
-------------------------------------

**Install the package without the root privilege**

>>> pip install --user caps

**Install the package with the root privilege**

>>> sudo pip install caps


.. _install_development:

Installing the current version
===============================

Nightly build packages are available at: 
http://nsap.intra.cea.fr/resources/ 

Install the python package with *pip*
-------------------------------------

**First find the package**
  * Choose the desired package, for instance `caps-0.0.1.dev.tar.gz`.
  * You have now the full url of the nightly build package you want to 
    install: 
    url = http://nsap.intra.cea.fr/resources/caps-0.0.1.dev.tar.gz 

**Install the package without the root privilege**

>>> pip install --user --verbose http://nsap.intra.cea.fr/resources/caps-0.0.1.dev.tar.gz

**Install the package with the root privilege**

>>> sudo pip install --verbose http://nsap.intra.cea.fr/resources/caps-0.0.1.dev.tar.gz

**When reinstalling locally the same package first do**

>>> pip uninstall capsul

**When installing a new version of the package**

>>> pip install --upgrade ...

Install the debian package with *dpkg*
--------------------------------------

**First find the package**
  * Choose the desired package, for instance `capsul-0.0.1.dev-1_all.tar.gz`.
  * You have now the full url of the nightly build package you want to 
    install:
    url = http://nsap.intra.cea.fr/resources/caps-0.0.1.dev-1_all.tar.gz

**Install the package with the root privilege**

>>> sudo dpkg -i http://nsap.intra.cea.fr/resources/caps-0.0.1.dev-1_all.tar.gz









