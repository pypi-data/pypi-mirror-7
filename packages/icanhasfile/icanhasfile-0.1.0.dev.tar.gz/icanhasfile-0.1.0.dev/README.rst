icanhasfile
===========

*COMPUTR, U HAS FILE. I CAN HAS IT?*

.. comment: pypi-split

icanhasfile is a Python module that helps you locate and operate on files using
glob searches.

installashun
------------

To install icanhasfile, simply:

.. code-block:: bash

 $ pip install --pre icanhasfile

usage
-----

To get the help dialog, run one of the following commands:

.. code-block:: bash

 $ icanhasfile --help
 $ icanhasfile -h
 $ icanhasfile -?

The general command syntax is below. For a list of options, see the help dialog.

.. code-block:: bash

 $ icanhasfile [options] <path> <filepattern>

examplez
--------
As an example, let's say we have the following directory structure:

.. code-block:: bash

 +-- pom.xml
 +-- LICENSE.txt
 |
 +-- dir1/
 |   |
 |   \-- pom.xml
 |
 +-- dir2/
 |   |
 |   +-- pom.xml
 |   +-- pom-changes.xml
 |   \-- version.txt
 |
 +-- dir3/
     |
     \-- context.xml

If you are searching for *pom.xml* and want to give the absolute path to the
top-level directory, issue the command below. You will be prompted to choose
from three matching files:

.. code-block:: bash

 $ icanhasfile /path/to/top-level/dir pom.xml
 [0] pom.xml
 [1] dir1/pom.xml
 [2] dir2/pom.xml
 Choose a number (q to quit):

If you are in the top-level directory and are searching for *pom\*.xml*, issue
the command below. You will be prompted to choose from four matching files:

.. code-block:: bash

 $ icanhasfile . 'pom*.xml'
 [0] pom.xml
 [1] dir1/pom.xml
 [2] dir2/pom-changes.xml
 [3] dir2/pom.xml
 Choose a number (q to quit):

By default, the selected file will be opened using your $EDITOR. However, you
can also provide a **--command** option to use a different command on your
path. In the example below, we will just *cat* out the file. Also, as it is
run in the icanhasfile source directory and there is only a single matching
file, the file is cat'd without asking the user to choose from multiple
matching files:

.. code-block:: bash

 $ icanhasfile.py --command cat . MANIFEST.in
 include LICENSE.txt
 include README.rst
