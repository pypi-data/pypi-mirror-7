=================================================================
pychangelog
=================================================================

.. # POST TITLE
.. # BEGIN BADGES

|pypi-version-badge| |license-badge| |pypi-downloads-badge|

.. |pypi-version-badge| image:: http://img.shields.io/pypi/v/pychangelog.svg
    :alt: [latest version on pypi]
    :target: https://pypi.python.org/pypi/pychangelog

.. |pypi-downloads-badge| image:: http://img.shields.io/pypi/dm/pychangelog.svg
    :alt: [downloads on pypi]
    :target: https://pypi.python.org/pypi/pychangelog

.. |license-badge| image:: http://img.shields.io/badge/license-GPLv3+-brightgreen.svg
    :alt: [GPLv3+]
    :target: https://www.gnu.org/licenses/gpl.html


.. # END BADGES


**pychangelog** is a python package which provides some simple utilities for parsing
and testing change logs, based on a simple standard format which is not really
documented anywhere. But you can look at the changelog for this project to get an
idea (in CHANGES.txt in the root of the source distribution).


.. contents:: **Page Contents**
    :local:
    :depth: 2
    :backlinks: top

tl;dr
---------------

What?
~~~~~~~~~~~~~~

Parses changelogs.

Install?
~~~~~~~~~~~~~

.. code:: bash

    $ pip install pychangelog

Or, from source:

.. code:: bash

    $ python setup.py install


Examples?
~~~~~~~~~~~~~~~~~~

Example changelog (in 'CHANGES.txt')::

    Pre Rel 4
        [M] Remove the doo_little function.
        [n] Add optional argument to frobnicate.
        [p] More bug fixes.

    Rel 3   - v1.1.0.0 - 2013-05-20
        [p] Bug fix in doo_little()
        [n] Added the frobnicate function in order to frob objects
            more easily.
        [s] Fixed up docs on doo_little.
        [p] Bug fix in some private functions

    Rel 2   - v1.0.0.1 - 2013-05-18
        [s] Documentation improvements.

    Rel 1   - v1.0.0.0 - 2013-05-15
        * Initial public release.
        * Provides the doo_little() function, and little else.


.. code:: python

    >>> import pychangelog
    >>> with open('CHANGES.txt', 'r') as f:
    ...     changelog = pychangelog.parse_plain_text(f)
    ...
    >>> changelog
    <pychangelog.ChangeLog object at 0x01F71A30>
    >>> len(changelog)
    4
    >>> for release in changelog:
    ...     print repr(release)
    ...
    <ReleaseInfo r1-1.0.0.0 (05/15/13)>
    <ReleaseInfo r2-1.0.0.1 (05/18/13)>
    <ReleaseInfo r3-1.1.0.0 (05/20/13)>
    <ReleaseInfo r4*>
    >>> r3 = changelog[2]
    >>> r3
    <ReleaseInfo r3-1.1.0.0 (05/20/13)>
    >>> r3.release_num
    3
    >>> r3.version
    (1, 1, 0, 0)
    >>> r3.year
    2013
    >>> r3.date
    datetime.date(2013, 5, 20)
    >>> len(r3)
    4
    >>> for change in r3:
    ...     print change
    ...
    [p] Bug fix in doo_little()
    [n] Added the frobnicate function in order to frob objectsmore easily.
    [s] Fixed up docs on doo_little.
    [p] Bug fix in some private functions
    >>> p = r3.patch
    >>> len(p)
    2
    >>> for patch_change in p:
    ...     print patch_change
    ...
    [p] Bug fix in doo_little()
    [p] Bug fix in some private functions
    >>> r3.append('[p] Another change I forgot to mention.')
    >>> len(p)
    3
    >>> len(r3)
    5
    >>> for patch_change in p:
    ...     print patch_change
    ...
    [p] Bug fix in doo_little()
    [p] Bug fix in some private functions
    [p] Another change I forgot to mention.
    >>>

Dependencies?
~~~~~~~~~~~~~~~~

pychangelog is developed against `python <https://www.python.org/>`_ version 2.7.

pychangelog also requires the `docit <https://pypi.python.org/pypi/docit>`_
package for its internals. If you install with :program:`pip`, this will be handled
automatically.

Some of the utilities in `pychangelog.tests` are optionally enhanced by the nose_
python package, but this is not strictly required. You can install nose with:

.. code:: bash

    $ pip install nose

To build the sphinx docs from source (as is), you'll need the `sphinx_rtd_theme`_:

.. code:: bash

    $ pip install sphinx_rtd_theme

Docs?
~~~~~~~~

* `Read The Docs (.org) <http://pychangelog.readthedocs.org/>`_
* `Python Hosted (.org) <http://pythonhosted.org/pychangelog/>`_


Misc.
---------------


Contact Information
~~~~~~~~~~~~~~~~~~~~~~~~

This project is currently hosted on `bitbucket <https://bitbucket.org>`_, 
at `https://bitbucket.org/bmearns/pychangelog <https://bitbucket.org/bmearns/pychangelog/>`_.
The primary author is Brian Mearns, whom you can contact through bitbucket at
`https://bitbucket.org/bmearns <https://bitbucket.org/bmearns>`_. 


Copyright and License
~~~~~~~~~~~~~~~~~~~~~~~~~~

\ ``pychangelog``\  is \ *free software*\ : you can redistribute it and/or modify
it under the terms of the \ **GNU General Public License**\  as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version. 



\ ``pychangelog``\  is distributed in the hope that it will be useful,
but \ **without any warranty**\ ; without even the implied warranty of
\ *merchantability*\  or \ *fitness for a particular purpose*\ .  See the
GNU General Public License for more details. 



A copy of the GNU General Public License is available in the
\ ``pychangelog``\ distribution under the file LICENSE.txt. If you did not
receive a copy of this file, see
`http://www.gnu.org/licenses/ <http://www.gnu.org/licenses/>`_. 

.. _sphinx_rtd_theme: https://github.com/snide/sphinx_rtd_theme
