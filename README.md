# ChessGame
**This game requires Python 3.7.7 (and further) and VLC (to play music).**

## Description

This is a personnel project that I created during the containment period to teach my girlfriend how to play chess, as she was far from me, on the other side of France... It features a server connecting two players who can play both on a local network or online via the internet. Please be advised that it is not a perfect work, as it is my first try at a complete game. The interface is definitely not optimal, as it uses OpenCV to create and display images, rather than a real computer window with buttons, layouts, etc. For example, I could have used Qt, but for this first version, I tried with what I already master: python and OpenCV.

## Installation

First of all, you need Python and `pip` working on your computer (download [here](https://www.python.org/downloads/)).

Secondly, you will also need VLC (download [here](https://www.videolan.org/vlc/index.fr.html)). It is important to add the path to VLC to your user PATH. The commande line will depend on your OS. On Windows, you can also do it from the configuration board.

When this is done, you can run the installation file corresponding to your OS :
1. On Windows : double-click `windows_install.bat`
2. On Linux : run linux_install.sh with the following commands.	
```bash
cd PATH/TO/INSTALLER
bash linux_install.sh
```
3. On MacOs : double-click `mac_install.command`


## How to play :
1. Set the server address in `player.py` (in the Game folder) and make sure the ports are opened on your server machine.
2. Run GameServer.py : `python GameServer.py` (on Windows, double-click `GameServer.bat`)
3. Run a first player file player.py :  `python player.py` (on Windows, double-click `play.bat`)
4. Run the second one from another machine connected to internet

PS : you can also play on a local network. Choose the IP addresses accordingly.









