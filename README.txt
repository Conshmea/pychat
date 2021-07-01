Python Project
==============
By Connor Schelbert
_________________________________

My project is a encrypted messaging client and server
It uses a type of RSA cipher Im still not sure exactly how the cipher works
I think most of the modules needed come pre-installed with python except kivy.
Note the public server should work.

Scripts
========

tkinter-client.py
--------------

-Needs Random, socket, threading and tkinter modules.

-Run in python 3.3 or higher.

How to Use
==========
-Run the script.
-Enter Server IP and Port in python shell and a tkinter GUI should open.
-Follow the instructions in the GUI.


kivy-client.py
-----------

- Needs sys, random, ast, multiprocessing, threading, time , Kivy(and all kivy sub modules) modules.

-Run in python 3.4 or higher and kivy 1.10.1 or higher.

How to Use
==========
-Run the script.
-A kivy GUI should open.
-Resize the GUI if need be on some screens it may appear the wrong size.
-Enter server Port, server Ip you can use The public server so you dont have to host your own.
-Enter a username and click join.
-It will take you to the chat screen.


server.py
---------

-Needs socket, threading, tkinter, random modules.

-Run in python 3.3 or higher

How to Use
==========
-Run the script it will start waiting for a connecction and thats it your all good to go