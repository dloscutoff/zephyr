How To Run Zephyr (Python 3 version)
David Loscutoff
8-3-12

1) Install Python 3.x. (NOTE: will not work with Python 2.x!) Configure it 
so that you can invoke it from the command line using the command 'python'.

2) Extract all files from the zip archive to a folder on the hard drive.

3) The Zephyr interpreter is zephyr.py. To run a Zephyr program, open the 
command line and type 'python', a space, the relative or absolute path to 
the Zephyr interpreter, a space, and the relative or absolute path to 
the Zephyr program you want to execute. Hit <enter>.



EXAMPLE (Windows XP/Vista/7):

Say the Zephyr implementation files are in C:\Zephyr and you want to execute
C:\Zephyr\Programs\helloWorld.zeph. If you are in the folder 
C:\Zephyr, you can execute this program by typing

python zephyr.py Programs\helloWorld.zeph

Alternately, if you are in the folder C:\Zephyr\Programs, we can 
execute this program by typing

python ..\zephyr.py helloWorld.zeph

or

python C:\Zephyr\zephyr.py helloWorld.zeph


Zephyr has not yet been tested on Unix. Note that most Unix systems still come 
with Python 2.x, so you would need to use the Python 2.x version of Zephyr or 
install Python 3.x.