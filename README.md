# PyWeb
PyWeb is a simple yet fully-funtional web browser made in Python. It is designed to do everything a good web browser needs to do as a viable alternative to Midori, NetSurf, and other small browsers. It is made with PyQt and Python 3, and will run on any platform that supports both of those. It renders with WebKit, so expect good quality. It is made to run on linux and not tested with Windows, although if you have Python 3 and PyQt4 or 5, it will work. You can use the provided package on Linux which will be provided starting at version 1.3 on the Releases page.

## Features
- Bookmarks
- Private Browsing
- Cookie Management
- Tabbed interface

## Planned features
- Better compatibility with WebGL

## Basic How-To
Change home page and search engine under bookmarks. Search engines currently supported and their value:
* Yahoo - yahoo
* Google - google
* DuckDuckGo - duck
* Bing - bing

## How to Install Manually
- Download PyQt 4 or 5 and Python 3 if you don't already have them
- Download the source code. Unzip to a directory.
- Open a terminal
- Run the command `chmod +x /path/to/PyWeb.py`.
- You can now run PyWeb as an excecutable.
- (optional) Create a .desktop shortcut (see [this article](https://linuxcritic.wordpress.com/2010/04/07/anatomy-of-a-desktop-file/))

## Issues
- under PyQt4, some Google webapps complain of an out-of date browser.
