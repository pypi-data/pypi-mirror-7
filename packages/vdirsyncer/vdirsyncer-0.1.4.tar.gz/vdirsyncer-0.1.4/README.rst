==========
vdirsyncer
==========

vdirsyncer synchronizes your calendars and addressbooks between two storages.
The supported storages are CalDAV, CardDAV, arbitrary HTTP resources and
`vdir <https://github.com/untitaker/vdir>`_.

It aims to be for CalDAV and CardDAV what `OfflineIMAP
<http://offlineimap.org/>`_ is for IMAP.

.. image:: https://travis-ci.org/untitaker/vdirsyncer.png?branch=master
    :target: https://travis-ci.org/untitaker/vdirsyncer

.. image:: https://coveralls.io/repos/untitaker/vdirsyncer/badge.png?branch=master
    :target: https://coveralls.io/r/untitaker/vdirsyncer?branch=master

While i use it daily and haven't experienced data loss (even when vdirsyncer
crashed), i don't know if the documentation is sufficient. If you have any
questions regarding the usage, feel free to open a new issue.

CardDAV/CalDAV Server Support
=============================

vdirsyncer is currently tested against the latest versions of Radicale and
ownCloud.

Radicale
--------

Radicale doesn't `support time ranges in the calendar-query of CalDAV/CardDAV
<https://github.com/Kozea/Radicale/issues/146>`_, so setting ``start_date`` and
``end_date`` in vdirsyncer's configuration will have no or unpredicted
consequences.

ownCloud
--------

ownCloud uses SabreDAV, which had problems detecting collisions and
race-conditions. The problems were reported and are fixed in SabreDAV's repo.
See `Bug #16 <https://github.com/untitaker/vdirsyncer/issues/16>`_ for more
information.

However, given that this is a problem with every setup involving ownCloud, and
that ownCloud is widely used, it apparently isn't big enough of a problem yet.

How to use
==========

vdirsyncer requires Python >= 2.7 or Python >= 3.3.

As all Python packages, vdirsyncer can be installed with ``pip``::

    pip install --user vdirsyncer

Then copy ``example.cfg`` to ``~/.vdirsyncer/config`` and edit it. You can use the
`VDIRSYNCER_CONFIG` environment variable to change the path vdirsyncer will
read the config from.

Run ``vdirsyncer --help``. If you experience any problems, consult the `wiki's
troubleshooting page
<https://github.com/untitaker/vdirsyncer/wiki/Troubleshooting>`_ or create a
new issue.

How to run the tests
====================

::

    sh build.sh install
    sh build.sh run

License
=======

vdirsyncer is released under the Expat/MIT License, see ``LICENSE`` for more
details.
