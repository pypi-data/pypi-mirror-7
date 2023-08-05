=================================================================
nosetp
=================================================================

.. # POST TITLE
.. # BEGIN BADGES

|pypi-version-badge| |license-badge| |pypi-downloads-badge|

.. |pypi-version-badge| image:: http://img.shields.io/pypi/v/nosetp.svg
    :alt: [latest version on pypi]
    :target: https://pypi.python.org/pypi/nosetp

.. |pypi-downloads-badge| image:: http://img.shields.io/pypi/dm/nosetp.svg
    :alt: [downloads on pypi]
    :target: https://pypi.python.org/pypi/nosetp

.. |license-badge| image:: http://img.shields.io/badge/license-GPLv3+-brightgreen.svg
    :alt: [GPLv3+]
    :target: https://www.gnu.org/licenses/gpl.html


.. # END BADGES


**nosetp** is a band-aid for some missing features in nose_.

**nosetp** provides the `nosetp <nosetp.commands.nosetp>` command for
setuptools_, which is just a wrapper around the :program:`nosetests` command provided
by default nose_, with some extra options. Specifically, the :opt:`--nosetp-chain`
option supresses the normal exit behavior of :program:`nosetests` so that it exits
if and only if tests are unsuccessful, otherwise it continues to execute any
other commands specified for :program:`setup.py`.


.. contents:: **Page Contents**
    :local:
    :depth: 2
    :backlinks: top

tl;dr
---------------

What?
~~~~~~~~~~~~~~

Some add-on functionlity for nose_.

Install?
~~~~~~~~~~~~~

.. code:: bash

    $ pip install nosetp

Or, from source:

.. code:: bash

    $ python setup.py install


Dependencies?
~~~~~~~~~~~~~~~~

nosetp is developed against `python <https://www.python.org/>`_ version 2.7.

nosetp also requires `docit <https://pypi.python.org/pypi/docit>`_
and nose_. If you install with :program:`pip`, these will be handled
automatically.

To build the sphinx docs from source (as is), you'll also need the `sphinx_rtd_theme`_:

.. code:: bash

    $ pip install sphinx_rtd_theme


Docs?
~~~~~~~~

* `Python Hosted (.org) <http://pythonhosted.org/nosetp/>`_


Misc.
---------------


Contact Information
~~~~~~~~~~~~~~~~~~~~~~~~

This project is currently hosted on `bitbucket <https://bitbucket.org>`_, 
at `https://bitbucket.org/bmearns/nosetp <https://bitbucket.org/bmearns/nosetp/>`_.
The primary author is Brian Mearns, whom you can contact through bitbucket at
`https://bitbucket.org/bmearns <https://bitbucket.org/bmearns>`_. 


Copyright and License
~~~~~~~~~~~~~~~~~~~~~~~~~~

\ ``nosetp``\  is \ *free software*\ : you can redistribute it and/or modify
it under the terms of the \ **GNU General Public License**\  as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version. 



\ ``nosetp``\  is distributed in the hope that it will be useful,
but \ **without any warranty**\ ; without even the implied warranty of
\ *merchantability*\  or \ *fitness for a particular purpose*\ .  See the
GNU General Public License for more details. 



A copy of the GNU General Public License is available in the
\ ``nosetp``\ distribution under the file LICENSE.txt. If you did not
receive a copy of this file, see
`http://www.gnu.org/licenses/ <http://www.gnu.org/licenses/>`_. 

.. _sphinx_rtd_theme: https://github.com/snide/sphinx_rtd_theme
.. _nose:   https://nose.readthedocs.org/
.. _setuptools: https://pythonhosted.org/setuptools/

