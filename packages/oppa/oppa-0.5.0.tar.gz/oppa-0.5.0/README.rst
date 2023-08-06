Oppa
====

Oppa is not PowerPoint like Application! It's lecture and presentation support tool. It allows free drawing with basic colors over every part of screen.

Usage
-----

Start oppa using:

.. code-block:: bash

	$ oppa --help
	usage: oppa [-h] [-o] [-z]

	optional arguments:
		-h, --help       show this help message and exit
		-o, --opaque     start in opaque mode
		-z, --minimized  start minimized

After starting oppa opens top level transparent window on which one can draw using left mouse button. Apart from drawing following actions (keys) are available: "r", "g", "b", "w" change drawing color to red, green, blue and white accordingly; "e" switches to eraser mode; "space" minimizes oppa; left click on icon in tray restores minimized oppa; "t" toggles transparency and "del" erases all drawing.

Windows
~~~~~~~

On Windows, after installation there are two programs (located in C:\\Python27\\Scripts): oppa and oppaw. First one is used to run oppa with command line window second without.

Requirements
------------

Oppa currently is developed and tested on Linux using Python 2.7. It requires PyGTK and Pycairo. For drawing in transparent window composited (either using XRender or OpenGL) screen is required - oppa will complain and use only opaque mode without composited screen.

Starting from version 0.5.0 there is experimental support for Windows (Windows 2000 and newer).

Installation
------------

The latest stable version is available to install using `pip <http://www.pip-installer.org/>`_:

.. code-block:: bash

	$ pip install oppa

Windows
~~~~~~~

Installation on Windows is essentially the same as on Linux. But first one need to have Python 2.7 with pip. Following steps might be used to install oppa from scratch on Windows:

1. Install Python using latest Python 2 from `python.org <https://www.python.org/downloads/windows/>`_ (default installation folder is C:\\Python27).
2. Install PyGTK and Pycairo using latest all-in-one installer from `pygtk.org <http://www.pygtk.org/downloads.html>`_.
3. Install latest setuptools using ez_setup.py from `setuptools installation <https://pypi.python.org/pypi/setuptools#windows-7-or-graphical-install>`_.

.. code-block:: bat

	C:\Python27>python.exe ez_setup.py

4. Install pip using get-pip.py from `pip installation <https://pip.pypa.io/en/latest/installing.html>`_.

.. code-block:: bat

	C:\Python27>python.exe get-pip.py

5. Install oppa using pip.

.. code-block:: bat

	C:\Python27\Scripts>pip.exe install oppa
