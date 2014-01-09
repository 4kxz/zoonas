Server configuration
====================

This section is not complete.

Salt basics
-----------

Install salt:

::

  $ apt-get install python-software-properties
  $ add-apt-repository ppa:saltstack/salt
  $ apt-get update
  $ apt-get install salt-minion

Add master IP to configuration file of minion ``/etc/salt/minion``:

::

  master: 42.32.99.264

Start minion:

::

  $ salt-minion

Accept the key in the master:

::

  $ salt-key -A

Test that commands reach the minions:

::

  $ salt ‘*’ test.ping

Enable master file server editing ``/etc/salt/master``:

::

  file_roots:
    base:
      - /srv/salt

Add basic settings in ``/srv/salt/top.sls``:

::

  base:
    ‘*’:
      - django

You need ``/srv/salt/django.sls``:

::

  /home/foo/django:
    file.recurse:
      - source: salt://src/django-files
