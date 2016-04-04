## There are two ways to run polyglot. The choice is yours. 
## Version 0.0.1
Initial Unstable Release. April 1st. 2016

These methods are for linux debian x86 or raspbian on a rpi. 

Get the system pre-requisites:  
`apt-get install python-git python-pip python3-pip libjpeg-dev`

## To run the Python module NON-compiled version
Clone the repository to a directory under the user you wish to run Polyglot. This will not run as root.
eg. /home/pi/ the following line will create a directory called Polyglot so no need to do that.  
`git clone https://github.com/UniversalDevicesInc/Polyglot.git`  
Move yourself into the Polyglot directory  
`cd Polyglot`

Install the Python required modules this does require root as we want to install them globally
for Python to access.  
`sudo pip install -r requirements.txt`  
Run Polyglot! Use -v for verbose or -vv for extra verbose logging. -c allows you to specifiy a config directory  
`python -m polyglot -v`

## To run the COMPILED version (aka all-in-one)
We will need to create a home for Polyglot  
`mkdir Polyglot && cd $_`

We still need the python pre-requisites:  
`sudo pip install -r https://github.com/UniversalDevicesInc/Polyglot/raw/unstable-release/requirements.txt`

Download the polyglot binary for your system. One of these:

For ARM (Raspberry Pi's)  
> https://github.com/UniversalDevicesInc/Polyglot/raw/unstable-release/bin/polyglot.linux-arm7l.pyz

For x86 Linux flavors (Built with Debian sid):  
> https://github.com/UniversalDevicesInc/Polyglot/raw/unstable-release/bin/polyglot.linux.x86_64.pyz

For MAC (Built on Yosemite)  
> https://github.com/UniversalDevicesInc/Polyglot/raw/unstable-release/bin/polyglot.osx.x86_64.pyz

Make the file executable. Use the filename you download this example is the ARM version.  
`chmod 755 polyglot.linux-arm7l.pyz`

Run Polyglot! Use -v for verbose or -vv for extra verbose logging. -c allows you to specifiy a config directory  
`./polyglot.linux-arm7l.pyz -v`

## Now What?
Now that Polyglot is running. Head to:  
`http://your_server_ip:8080`

Login with admin/admin and configure your ISY and Polyglot settings.
	
## Extras
	
Init script: To start on boot. 

If you are running the module you already have the polyglot.server file in your Polyglot root folder.  
If not then get it like so:  
`wget https://github.com/UniversalDevicesInc/Polyglot/raw/unstable-release/polyglot.service`

Edit the file polyglot.server with your favorite editor.  
Modify WorkingDirectory to be your root Polyglot directory. eg. /home/pi/Polyglot  
`WorkingDirectory=/home/pi/Polyglot`  
Modify ExecStart to be how you start it. Full path needed.  
For pure Python(Non-compiled):  
`ExecStart=/usr/bin/python -m polyglot -v`  
For the compiled binary:  
`ExecStart=/home/pi/Polyglot/polyglot.linux-arm7l.pyz -v`  

Change the user to the user account that will run polyglot (NOT ROOT)  
`User=pi`  
	
Copy polyglot.service to /lib/systemd/system/ You need sudo as /lib/systemd/system is a system directory.  
```sudo cp /home/pi/Polyglot/polyglot.service /lib/systemd/system/```

Enable systemctl (Make sure polyglot isn't already running):  
```sudo systemctl enable polyglot
sudo systemctl start polyglot```
	
Log files are found under config/polyglot.log. To watch the live action:  
```tail -fn 50 /home/pi/Polyglot/config/polyglot.log```

# Adding Poly's  
Next if you need to get any NON built-in Polyglots (Like any of Einstein.42 or Jimbo's)  
Assuming you are in the Polyglot directory mentioned above, eg. /home/pi/Polyglot/  
```cd config/node_servers```  
You will create the specific Poly's here under sub folders.
Follow the instructions for your Poly for further details. 
