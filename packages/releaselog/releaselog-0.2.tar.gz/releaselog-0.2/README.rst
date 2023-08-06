##########
releaselog
##########

releaselog is a tool for generating release notes from git logs for `taskotron <http://fedoraproject.org/wiki/Taskotron>`_. Currently it only supports a very small and fragile setup specific to Taskotron. This script might however be useful for other projects as well.

Installation
------------

.. code:: bash

    pip install releaselog

Or

.. code:: bash
  
    python setup.py install

Usage
-----

releaselog was originally meant to generate RST files for use with `Sphinx <http://sphinx-doc.org>`_, but could be used for pretty much anything else that wants RST. Adding this to your project should be simple.

Assumptions:
 - project uses sphinx for documentation
 - sphinx uses a 'docs' directory

From your 'docs' directory, run "releaselog". The default is to drop down into the parent directory and examine git logs. You can optionally pass in a path "releaselog <path>" and it will add the docs to <path>/docs/source.
