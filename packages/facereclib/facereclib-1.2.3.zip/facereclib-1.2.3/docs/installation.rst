.. vim: set fileencoding=utf-8 :
.. author: Manuel Günther <manuel.guenther@idiap.ch>
.. date: Thu Sep 20 11:58:57 CEST 2012

.. _installation:

=========================
Installation instructions
=========================

.. note::
  This documentation includes several ``file://`` links that usually point to files or directories in your source directory.
  When you are reading this documentation online, these links won't work.
  Please read `Generate this documentation`_ on how to create this documentation including working ``file://`` links.

Download
--------

|project|
~~~~~~~~~
To have a stable version of the |project|, the safest option is to go to the FaceRecLib_'s web page on Pypi_ and download the latest version.

Nevertheless, the library is also available as a project of `Idiap at GitHub`_.
To check out the current version of the |project|, go to the console, move to any place you like and call:

.. code-block:: sh

  $ git clone git@github.com:idiap/facereclib.git

Be aware that you will get the latest changes and that it might not work as expected.

Bob
~~~

The |project| is a satellite package of Bob_, where most of the image processing, feature extraction, and face recognition algorithms, as well as the evaluation techniques are implemented.
To run properly, |project| requires Bob_ at least in version 1.2.0.
If you have not installed Bob_ or your version is to old, please visit Bob_'s web page and download the latest version.
If you prefer not to install Bob_ in its default location, you have to adapt the ``prefixes`` of the buildout.cfg_ configuration file, which sits in the main directory of the |project|.

.. note::
  Currently, there is no MS Windows version of Bob_.

Usually, all possible database satellite packages (called ``xbob.db.[...]``) are automatically downloaded from PyPI_.
If you don't want to download the databases, please edit the ``eggs`` section of the buildout.cfg_ configuration file by removing the databases that you don't want.

The ``gridtk`` tool kit is mainly used for submitting submitting jobs to Idiap_'s SGE_ grid.
The latest version also supports to run jobs in parallel on the local machine.
You can safely remove this line from the buildout.cfg_ if you are not at Idiap and if you don't want to launch your experiments in parallel.


The CSU Face Recognition Resources
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Two open source algorithms are provided by the `CSU Face Recognition Resources`_, namely the LRPCA and the LDA-IR algorithm.
For these algorithms, optional wrapper classes are provided in the xfacereclib.extension.CSU_ satellite package.
By default, this package is disabled.
To enable them, please call::

  $ bin/buildout -c buildout-with-csu.cfg

after downloading and patching the CSU resources, and updating the ``sources-dir`` in the **buildout-with-csu.cfg** file -- as explained in xfacereclib.extension.CSU_.


Image databases
~~~~~~~~~~~~~~~

With the |project| you will run face recognition experiments using some default facial image databases.
Though the verification protocols are implemented in the |project|, the images (and the hand-labelled annotations) are **not included**.
To download the image databases, please refer to the according Web-pages.

For a start, you might want to try the small, but freely available image database called the `AT&T database`_ (formerly known as the ORL database).
Other database URL's will be given in the :ref:`databases` section.

Set-up your |project|
---------------------

Now, you have everything set up such that you can continue to set up the |project|.
To do this, we use the BuildOut_ system.
To proceed, open a terminal in your |project| main directory and call:

.. code-block:: sh

  $ python bootstrap.py
  $ bin/buildout

The first step will generate a `bin <file:../bin>`_ directory in the main directory of the |project|.
The second step automatically downloads all dependencies (except for Bob_) of the |project| and creates all required scripts that we will need soon.


Test your installation
~~~~~~~~~~~~~~~~~~~~~~

One of the scripts that were generated during the bootstrap/buildout step is a test script.
To verify your installation, you should run the script by calling:

.. code-block:: sh

  $ bin/nosetests

Some of the tests that are run require the images of the `AT&T database`_ database.
If the database is not found on your system, it will automatically download and extract the `AT&T database`_ a temporary directory (which will not be erased).

To avoid the download, please:

1. Download the `AT&T database`_ database and extract it to the directory of your choice.
2. Set an environment variable ``ATNT_DATABASE_DIRECTORY`` to the directory, where you extracted the database to.
   For example, in a ``bash`` you can call

.. code-block:: sh

  $ export ATNT_DATABASE_DIRECTORY=/path/to/your/copy/of/atnt

.. note::
  To set the directory permanently, you can also change the ``atnt_default_directory`` in the file `facereclib/utils/tests.py <file:../facereclib/utils/tests.py>`_.
  In this case, there is no need to set the environment variable any more.

In case any of the tests fail for unexplainable reasons, please file a bug report through the `GitHub bug reporting system`_.

.. note::
  Currently, all tests should pass using Bob_ in version 1.2.1.
  In other versions, some of the tests may fail (currently I know of ISV and JFA tests that use different random initializations in Bob 1.2.0.)


Generate this documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

To generate this documentation, you call:

.. code-block:: sh

  $ bin/sphinx-build docs sphinx

Afterwards, the documentation is available and you can read it, e.g., by using:

.. code-block:: sh

  $ firefox sphinx/index.html


.. _buildout.cfg: file:../buildout.cfg

.. include:: links.rst
