..
    This file is part of lazr.smtptest.

    lazr.smtptest is free software: you can redistribute it and/or modify it
    under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, version 3 of the License.

    lazr.smtptest is distributed in the hope that it will be useful, but
    WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
    or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
    License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with lazr.smtptest.  If not, see <http://www.gnu.org/licenses/>.

========================
Hacking on lazr.smtptest
========================

These are guidelines for hacking on the lazr.smtptest project.  But first,
please see the common hacking guidelines at:

    http://dev.launchpad.net/Hacking


Getting help
============

If you find bugs in this package, you can report them here:

    https://launchpad.net/lazr.smtptest

If you want to discuss this package, join the team and mailing list here:

    https://launchpad.net/~lazr-users

or send a message to:

    lazr-users@lists.launchpad.net


Running the tests
=================

The tests suite requires tox_ and nose_ and is compatible with both Python 2
and Python 3.  To run the full test suite::

    $ tox

.. _nose: https://nose.readthedocs.org/en/latest/
.. _tox: https://testrun.org/tox/latest/
