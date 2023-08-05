=================================================================
docit
=================================================================

.. # POST TITLE
.. # BEGIN BADGES

|pypi-version-badge| |license-badge| |pypi-downloads-badge|

.. |pypi-version-badge| image:: http://img.shields.io/pypi/v/docit.svg
    :alt: [latest version on pypi]
    :target: https://pypi.python.org/pypi/docit

.. |pypi-downloads-badge| image:: http://img.shields.io/pypi/dm/docit.svg
    :alt: [downloads on pypi]
    :target: https://pypi.python.org/pypi/docit

.. |license-badge| image:: http://img.shields.io/badge/license-GPLv3+-brightgreen.svg
    :alt: [GPLv3+]
    :target: https://www.gnu.org/licenses/gpl.html


.. # END BADGES


**docit** is a python package which provides some simple tools to use with sphinx
autodoc to control whether or not members are included in the documentation or not.


.. contents:: **Page Contents**
    :local:
    :depth: 2
    :backlinks: top

tl;dr
---------------

What?
~~~~~~~~~~~~~~

A `sphinx <http://sphinx-doc.org/>`_ extension to control autodoc for individual
members.

Install?
~~~~~~~~~~~~~

.. code:: bash

    $ pip install docit

Or, from source:

.. code:: bash

    $ python setup.py install


Examples?
~~~~~~~~~~~~~~~~~~

.. todo::
    Example code

.. code:: python

    >>> import docit
    >>>

Dependencies?
~~~~~~~~~~~~~~~~

docit is developed against `python <https://www.python.org/>`_ version 2.7.

To build the sphinx docs from source (as is), you'll need the `sphinx_rtd_theme`_:

.. code:: bash

    $ pip install sphinx_rtd_theme


Docs?
~~~~~~~~

* `Read The Docs (.org) <http://docit.readthedocs.org/>`_
* `Python Hosted (.org) <http://pythonhosted.org/docit/>`_


Misc.
---------------


Contact Information
~~~~~~~~~~~~~~~~~~~~~~~~

This project is currently hosted on `bitbucket <https://bitbucket.org>`_, 
at `https://bitbucket.org/bmearns/docit <https://bitbucket.org/bmearns/docit/>`_.
The primary author is Brian Mearns, whom you can contact through bitbucket at
`https://bitbucket.org/bmearns <https://bitbucket.org/bmearns>`_. 


Copyright and License
~~~~~~~~~~~~~~~~~~~~~~~~~~

\ ``docit``\  is \ *free software*\ : you can redistribute it and/or modify
it under the terms of the \ **GNU General Public License**\  as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version. 



\ ``docit``\  is distributed in the hope that it will be useful,
but \ **without any warranty**\ ; without even the implied warranty of
\ *merchantability*\  or \ *fitness for a particular purpose*\ .  See the
GNU General Public License for more details. 



A copy of the GNU General Public License is available in the
\ ``docit``\ distribution under the file LICENSE.txt. If you did not
receive a copy of this file, see
`http://www.gnu.org/licenses/ <http://www.gnu.org/licenses/>`_. 

.. _sphinx_rtd_theme: https://github.com/snide/sphinx_rtd_theme
