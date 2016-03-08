# This script will take the default Raspbian Wheezy linux distribution for the
# Raspberry Pi and alter it to be the custom distribution for Polyglot.
#
# Must be run with sudo
#

# remove unneeded packages
apt-get install deborphan
apt-get autoremove --purge libx11-.* lxde-.* raspberrypi-artwork xkb-data omxplayer penguinspuzzle sgml-base xml-core alsa-.* cifs-.* samba-.* fonts-.* desktop-* gnome-.*
apt-get autoremove --purge $(deborphan)
apt-get autoremove --purge
apt-get autoclean

# install dependencies
apt-get install python-pip python-dev build-essential
pip install cython

# setup pi user
echo -e "Z^YE^mp5tGSPogm:pi" | chpasswd
mkdir ~/.ssh
chmod 700 ~/.ssh
cd ~/.ssh
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCu7fzuXs9tL6s1JNBE/dCvZsl+6TiU2SaOxOMDlAtJds1ufXEBEQjXoxXSggtpADCoF47XLd8Q9FQ0MgptsZNH2bywmlbQcI1alx6zOj9JCFROz28H5ygPj8K3UTDrTX2ugD+i2wPaVvGxn4MGEgGH7ePD6ae/GNYYNCXS63n+/RGf52EX/u3lQBvL7XURjvbw9+Ilepw9AbaF22GbT0S8ZRjMNJ8SQEvbr1Q7sR0tmU2YcrQjWKfGECs0PWlmTl6wNZUDTijLFZY2b+xoAn2h5ahRuHUVvOkU7Jlyiaq5Y8tYz1dkpRk9bPbQd1GosXftHDYivYmUcx2gJEqQb27xvmMuOngXBvdxmzATyWqfnF0ygGwnGl8+TRm1yo4Y8Zgp+EPmZOL3k7EQVUSIk+kuiPLdEDBr2neqDGXJpOBusoKlgQDqqgB7ihUTW3/KTZY8hCyu/JXv1mp9nWbU3AnFoS22bomK/cVcQPEUHW7abVf6rNm1eJz7rk6LBnF+ZTNrjI7h4dDv7cM695aV+IClZEI0KO4eTj1ntRCiRBg+rGpCPjIR4WACKwqOrNfWk1poiPPDCft3RU4XyjCjdwtflnI090/OxqXMk+c4AA62PFF6T4VRph+RL0TMKyIc3VTmCTdpFMknVhi2w8WPKM9lPoSS8VoIqJjHrsJYpDGRfw== pi@raspberrypi" > id_rsa.pub
ln -s id_rsa.pub authorized_keys


## Distribution Details
# user: pi
# password: Z^YE^mp5tGSPogm
