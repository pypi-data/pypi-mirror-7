=======
udiskie
=======

|Version| |Downloads| |License|

*udiskie* is a simple daemon that uses UDisks_ to automatically mount
removable storage devices. This daemon comes with optional mount
notifications and GTK tray icon. It also provides a user level CLI for
mount and unmount operations.


Usage
-----

Start the automount and notification daemon:

.. code-block:: bash

    # the optional tray icon requires PyGTK
    udiskie --tray  

Mount or unlock a specific device manually:

.. code-block:: bash

    udiskie-mount /dev/sdb1

Unmount or remove a specific device manually:

.. code-block:: bash

    udiskie-umount /media/<device-name>

See the man page for further instructions


Dependencies
------------

Unfortunately, *udiskie* has dependencies that can not be automatically
downloaded and installed from PyPI:

- UDisks_ required for all operation modes. UDisks2 support is experimental
  and has to be requested explicitly via the command line parameter ``-2``.
- dbus-python_ required for all operation modes
- PyGObject_ to run the automount/notification daemon (provides the main loop)
- notify2_ or notify-python_ for mount notifications
- Zenity_ to show a password prompt to unlock LUKS devices
- PyGTK_ to show the system tray icon

.. _UDisks: http://www.freedesktop.org/wiki/Software/udisks
.. _dbus-python: http://dbus.freedesktop.org/doc/dbus-python/
.. _PyGObject: http://ftp.gnome.org/pub/gnome/sources/pygobject/
.. _notify-python: http://www.galago-project.org/files/releases/source/notify-python/
.. _notify2: https://pypi.python.org/pypi/notify2
.. _Zenity: http://freecode.com/projects/zenity
.. _PyGTK: http://www.pygtk.org


Permissions
-----------

*udiskie* requires permission for the following PolicyKit_ actions:

.. _PolicyKit: http://www.freedesktop.org/wiki/Software/PolicyKit

- ``org.freedesktop.udisks.filesystem-mount`` for mounting and unmounting
- ``org.freedesktop.udisks.luks-unlock`` to unlock LUKS devices
- ``org.freedesktop.udisks.drive-eject`` to eject drives
- ``org.freedesktop.udisks.drive-detach`` to detach drives

These are usually granted when using a desktop environment. If your login
session is not properly activated you may need to customize your PolicyKit
settings. Create the file
``/etc/polkit-1/localauthority/50-local.d/10-udiskie.pkla`` with the
following contents:

.. code-block:: cfg

    [udiskie]
    Identity=unix-group:storage
    Action=org.freedesktop.udisks.filesystem-mount;org.freedesktop.udisks.luks-unlock;org.freedesktop.udisks.drive-eject;org.freedesktop.udisks.drive-detach
    ResultAny=yes

This configuration allows all members of the *storage* group to run udiskie.

Alternatively, change the setting for ``allow_inactive`` to *yes* in the
file ``/usr/share/polkit-1/actions/org.freedesktop.udisks.policy``:

.. code-block:: xml

    <action id="org.freedesktop.udisks.filesystem-mount">
        ...
        <allow_inactive>yes</allow_inactive>
        ...
    </action>

    ...

Do this for all relevant actions.

Note that UDisks2 uses another set of permissions, see
``/usr/share/polkit-1/actions/org.freedesktop.udisks2.policy``.


GTK icons
---------

*udiskie* comes with a set of themeable custom Tango-style GTK icons for its
tray icon menu. The installer tries to install the icons into GTK's default
hicolor theme. Typically this is located in ``/usr/share/icons/hicolor``. If
you have any problems with this or you need a custom path you can manually do
it like so:

.. code-block:: bash

    cp ./icons/scalable /usr/share/icons/hicolor -r
    gtk-update-icon-cache /usr/share/icons/hicolor

When doing a local installation, for example in a virtualenv, you can
manually change the installation prefix for the icon data files like so:

.. code-block:: bash

    python setup.py install --install-data ~/.local

The icons roughly follow the `Tango style guidelines`_. Some icons incorporate
the CDROM icon of the base icon theme of the `Tango desktop project`_
(released into the public domain).

.. _`Tango style guidelines`: http://tango.freedesktop.org/Tango_Icon_Theme_Guidelines
.. _`Tango desktop project`: http://tango.freedesktop.org/Tango_Desktop_Project


Contributing
------------

*udiskie* is developed on github_. Feel free to contribute patches as pull
requests here.

Try to be consistent with the PEP8_ guidelines. Add `unit tests`_ for all
non-trivial functionality if possible. `Dependency injection`_ is a great
pattern to keep modules flexible and testable.

Commits should be reversible, independent units if possible. Use descriptive
titles and also add an explaining commit message unless the modification is
trivial. See also: `A Note About Git Commit Messages`_.

.. _github: https://github.com/coldfix/udiskie
.. _PEP8: http://www.python.org/dev/peps/pep-0008/
.. _`unit tests`: http://docs.python.org/2/library/unittest.html
.. _`Dependency injection`: http://www.youtube.com/watch?v=RlfLCWKxHJ0
.. _`A Note About Git Commit Messages`: http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html


Contact
-------

You can use the `github issues`_ to report any issues you encounter, ask
general questions or suggest new features. There is also a public `mailing
list`_ on sourceforge if you prefer email.

.. _`github issues`: https://github.com/coldfix/udiskie/issues
.. _`mailing list`: https://lists.sourceforge.net/lists/listinfo/udiskie-users


.. |Version| image:: https://pypip.in/v/udiskie/badge.png
   :target: https://pypi.python.org/pypi/udiskie/
   :alt: Latest Version

.. |Downloads| image:: https://pypip.in/d/udiskie/badge.png
   :target: https://pypi.python.org/pypi/udiskie/
   :alt: Downloads

.. |License| image:: https://pypip.in/license/udiskie/badge.png
   :target: https://pypi.python.org/pypi/udiskie/
   :alt: License
