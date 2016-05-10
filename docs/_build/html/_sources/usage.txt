Usage
=====

Installation
~~~~~~~~~~~~

Polyglot ships in a compiled, system dependent container. To install, place
this file in the desired directory on your system and launch.

.. code-block:: bash

    ./polyglot.pyz

This will launch Polyglot and create a directory titled *config* in the current
directory. Polyglot will store all of its configuration and its log inside of
this directory. You may specify a manual path for this directory using the
command line flags.

The following are all of the available flags at the command line.

.. code-block:: bash

    -h, --help            show this help message and exit
    -c CONFIG_DIR, --config CONFIG_DIR
                          Polyglot configuration directory
    -v, --verbose         Enable verbose logging
    -vv                   Enable very verbose logging

While running in its default mode, Polyglot will log all warnings and errors.
Verbose logging will include info messages. Very verbose mode adds debug
messages that could be useful when developing a new node server.

Once Polyglot is running, the user interface may be accessed by opening your
favorite browser and navigating to::

    http://localhost:8080

The default username and password are both *admin*.

If you are accessing the frontend from another machine, replace *localhost*
with the IP Address or URL of the machine running Polyglot. If you are having
trouble accessing the user interace from a remote machine, check your firewall
settings.

User Interface
~~~~~~~~~~~~~~
.. image:: _static/screenshots/settings.png
   :scale: 50 %
   :align: center

The user interface is designed to be simple and intuitive to use. Pictured
above is the settings page. Using the menu bar on the left, new node servers
can be added and existing node servers may be monitored. The button on the
bottom of the menu will open Polyglot's log in a new browser window.

The user interface is fully compatible with both tablet and mobile devices.

Settings
~~~~~~~~

The settings view allows the user to alter settings for Polyglot's HTTP server
as well as Polyglot's connection to the ISY controller. It is recomended that
the username and password are changed from the default. If a new different port
is desired, it may be set in the *Server Configuration* block.

It is also necessary to set the username, password, host name, and port
required for connecting to the ISY. These may be configured in the *ISY
Configuration* block.

Adding Node Server
~~~~~~~~~~~~~~~~~~

.. image:: _static/screenshots/add_ns.png
   :scale: 35 %
   :align: center

To add a node server, navigate to the *Add Node Server* view using the menu.
This view is pictured above.

Populate this form with the details for the new node server. Select a type from
all installed types using the drop down. Give the node server any name allows
for easy recognition. Finally, populate the *Node Server ID* field with an ID
that is available in the ISY. Press *ADD* when complete.

The node server will now be available in Polyglot. You may navigate to it using
the menu. The node server view in Polyglot will show the Node Server ID, Base
URL, and allow for the Profile to be downloaded.

In order to access the node server from the ISY, it must be added to the ISY.
To do this, inside of the ISY console, navigate to Node Servers then Configure
then the Node Server ID that was set while creating the node server. This will
open a dialog that accepts all the information from the node server view.
Populate this with the Profile Name and Base URL from the node server view.
The User ID, Passsword, Host Name, and Port here must be the values used for
connecting to Polyglot. Timeout may be left as 0, and the Isy User should be
set to the appropriate user ID that was configured in Polyglot. If you are
unsure, use 0.

Click the *Upload Profile* button and navigate to the zip file obtained from
Polyglot's node server view. Once this has been uploaded, click *Ok* and
restart the ISY controller. Once the ISY has fully rebooted, restart the
node server in Polyglot using the node server view.

Managing Node Servers
~~~~~~~~~~~~~~~~~~~~~

.. image:: _static/screenshots/view_ns.png
   :scale: 50 %
   :align: center

Clicking a Node Server in the menu will activate the node server view. In this
view, there is a menu bar at the top. This menu bar will indicate is the node
server is Running or Stopped. It also provides buttons to download the profile,
restart the node server, or delete the node server.

Also in this view are instructions for using this node server. Different node
servers may have their own instructions on how to use them in the ISY. Any
open-source, third party libraries that were used for the development of the
node server are also credited here.

If the node server were to crash, a red X will appear next to it in the menu
and it will be indicated in the menu bar on the top of the node server view.
If this happens, it is best to save the log for debugging and then restart the
node server using the button in the menu bar.

Viewing Polyglot Log
~~~~~~~~~~~~~~~~~~~~

There is a file icon below all the main menu items. Clicking this icon will
open Polyglot's log in a new browser window. This log file is critical for
debugging issues with Polyglot.
