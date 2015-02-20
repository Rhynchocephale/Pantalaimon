Pantalaimon: daemon & cron
===================


What it does
-------------

Pantalaimon is a python code that copies pictures in a specified folder into another, sorts them according to the date they were taken, and generates an HTML gallery. It can be run either as a cron or a daemon. Only works on Linux systems.

### In details ###
####The copying process ####
 - Copies pictures from one directory to another, and sort them by date in the meantime. The date where the picture was taken is extracted from the metadata; if not present, the date taken into account will be the one of the last modification of the file. An option can be enabled to delete the original once the copy is done.
 - In the output folder, sorts the pictures in an arborescence of folders: one folder per year, one subfolder per month.
 - Pictures are renamed when moved, and get a new name in the format *dd-mm_hh:mm (x)*, where x is a number used to differentiate between pictures taken at the same minute, if there are more than one. Renaming can be deactivated.
 - When copying a picture, checks that the picture is not already present. Otherwise, does not copy it.
 - Looks recursively into every subfolder of the input folder, and looks for every picture in them.

####The gallery ####
 - Drop-down menu.
 - Responsive design.
 - Clicking on a picture displays it in full size.
 - Shows the date the picture was taken when hovering.
 - The size of the images in the gallery is configurable.
 - Screenshots will be added.

Installing
-------------

- Clone the directory in a folder of your choice
- Edit Pantalaimon/config so that it fits to your needs
- Move Pantalaimon folder to /tmp
- Install all relevant libraries (will be completed later)

How to run it
-------------

Open your favorite console and follow the instructions:

  | Daemon | Cron
---- | -------- | ---
Start | Type **python /path/to/folder/Daemon.py start** | Type **crontab -e** and append the following line to the file that has just opened (spacing matters): __* * * * * python /path/to/folder/Cron.py__
Stop | Type **python /path/to/folder/Daemon.py stop** | Type **crontab -e** and remove the line you previously added.
