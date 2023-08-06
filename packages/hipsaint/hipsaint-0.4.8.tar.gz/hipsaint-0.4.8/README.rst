==========
 HipSaint
==========

Push your nagios notifications to HipChat using a simple command line tool.

.. image:: https://travis-ci.org/hannseman/hipsaint.png?branch=master
  :target: https://travis-ci.org/hannseman/hipsaint
   
.. image:: https://pypip.in/d/hipsaint/badge.png
  :target: https://pypi.python.org/pypi/hipsaint

Implements `HipChat message API`_.

.. _`hipchat message API`: https://www.hipchat.com/docs/api/method/rooms/message

Inspired by https://gist.github.com/2418848.

---------
 Install
---------

Through pip:

.. code-block:: bash

    pip install hipsaint


Or clone and simply run:

.. code-block:: bash

    python setup.py install

-------
 Usage
-------

Assuming you use Nagios 3 add the following sections to commands.cfg with ``<TOKEN>`` and ``<ROOM_ID>`` specified and macros delimited by ``|``::

    define command {
        command_name    notify-host-by-hipchat
        command_line    hipsaint --token=<TOKEN> --room=<ROOM_ID> --type=host --inputs="$HOSTNAME$|$LONGDATETIME$|$NOTIFICATIONTYPE$|$HOSTADDRESS$|$HOSTSTATE$|$HOSTOUTPUT$" -n
    }
    define command {
        command_name    notify-service-by-hipchat
        command_line    hipsaint --token=<TOKEN> --room=<ROOM_ID> --type=service --inputs="$SERVICEDESC$|$HOSTALIAS$|$LONGDATETIME$|$NOTIFICATIONTYPE$|$HOSTADDRESS$|$SERVICESTATE$|$SERVICEOUTPUT$" -n
    }

To send less verbose messages to hipchat set the ``--type`` flag to either ``short-host`` or ``short-service``.

Additional commands is available through:

.. code-block:: bash

    hipsaint --help


Edit the Nagios contacts.cfg file by adding or editing an existing user and adding the notification commands created above::

    define contact {
            ....
            .....
            service_notification_commands   notify-service-by-hipchat
            host_notification_commands      notify-host-by-hipchat
            email   /dev/null
    }
