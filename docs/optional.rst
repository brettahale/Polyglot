Optional Components
===================

Docker
~~~~~~

These are the instructions for Docker configuration provided by
UDI forum and Polyglot contributor i814u2.

Original Threads:

http://forum.universal-devices.com/topic/19807-%20polyglot-docker-%20image/#entry187776
http://forum.universal-devices.com/topic/19807-%20polyglot-docker-%20image/page-2

linux x86_64 instructions
-------------------------
Create a file named "Dockerfile" (case-sensitive) and place these
commands in there:

.. code-block:: bash

  ARG binfile=polyglot.linux.x86_64.pyz
  ARG user=polyglot
  ARG group=polyglot
  ARG uid=1000
  ARG gid=1000


  RUN addgroup -g ${gid} ${group} \
      && adduser -h /home/${user} -s /bin/sh -G ${group} -D -u ${uid} ${user}


  WORKDIR /home/${user}
  COPY custom.txt .


  RUN pip install --upgrade pip \
  && pip install -r https://raw.githubusercontent.com/UniversalDevicesInc/Polyglot/unstable-release/requirements.txt \
  && while read line; do $line; done < custom.txt


  RUN wget https://github.com/UniversalDevicesInc/Polyglot/raw/unstable-release/bin/${binfile}-P Polyglot \
  && chown -R ${user}:${group} /home/${user} \
  && chmod 755 /home/${user}/Polyglot/${binfile}


  USER ${user}
  WORKDIR /home/${user}/Polyglot
  ENTRYPOINT ["./polyglot.linux.x86_64.pyz","-v"]

Create a file named "custom.txt" and add whatever python modules and node servers you'd like installed.
Here is the example I have for adding Sonos and Nest:

.. code-block:: bash

  pip install soco
  pip install python-nest
  git clone https://github.com/Einstein42/sonos-polyglot Polyglot/config/node_servers/sonos-polyglot
  git clone https://github.com/Einstein42/nest-polyglot Polyglot/config/node_servers/nest-polyglot

Create a folder to store your config:

.. code-block:: bash

  mkdir -p ~/docker/polyglot

(If you already have polyglot up and running, backup your config folder and then just point this to your existing config folder instead of the one above. This should work, but always make a backup.)

The image is built by running this command (from the folder where you Dockerfile and custom.txt files are located):

.. code-block:: bash

  docker build -t polyglot .

After that completes, you should be able to run a command like this:

.. code-block:: bash

  docker run -d --name=polyglot -v ~/docker/polyglot:/home/polyglot/Polyglot/config --net=host -t polyglot-docker

The polyglot page should be available via your docker host machine's IP and port 8080. If that needs to change, allow it to start, then stop the container (docker stop polyglot), edit the configuration.json in the config folder on your docker host. Then start it back up (docker start polyglot).
I chose to use the non-compiled variation so that it would run across more systems. Another item I'd like to improve is only using the compiled version in order to save space.

**Ready to use image for linux x86_64**

Run this command, assuming you already have docker setup and running for your user on your linux machine.

.. code-block:: bash

  mkdir -p ~/docker/polyglot && docker run -d --name=polyglot -v ~/docker/polyglot:/home/polyglot/Polyglot/config --net=host -t i814u2/udi-polyglot

Then re-pull the image in order to update it, and re-create the container (this will also start the container, of course):

.. code-block:: bash
  docker pull i814u2/udi-polyglot && docker run -d --name=polyglot -v ~/docker/polyglot:/home/polyglot/Polyglot/config --net=host -t i814u2/udi-polyglot
