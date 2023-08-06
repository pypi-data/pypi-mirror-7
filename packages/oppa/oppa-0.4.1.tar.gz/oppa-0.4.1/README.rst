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

Requirements
------------

Oppa currently is developed and tested on Linux using Python 2.7. It requires PyGTK and Pycairo. For drawing in transparent window composited (either using XRender or OpenGL) screen is required - oppa will complain and use only opaque mode without composited screen.

Installation
------------

The latest stable version is available to install using `pip <http://www.pip-installer.org/>`_:

.. code-block:: bash

	$ pip install oppa
