radish
======

    ``radish`` is a "Behavior-Driven Developement"-Tool written in
    python Version: 0.01.29

--------------

**Author:** Timo Furrer tuxtimo@gmail.com\  **License:** GPL
**Version:** 0.01.31

Table of contents
-----------------

1. `What is radish <#whatis>`__
2. `Installation <#installation>`__

   1. `Missing dependencies <#missing_dependencies>`__
   2. `Simple installation with pip <#installation_pip>`__
   3. `Manual installation from source <#installation_source>`__
   4. `Update source installation <#installation_update>`__
   5. `Install on Windows <WINDOWS_INSTALLATION_GUIDE.md>`__

3. `How to use? <#usage>`__
4. `Writing tests <#write_tests>`__
5. `Contribution <#contribution>`__
6. `Infos <#infos>`__

What is ``radish`` ?
--------------------

``radish`` is a "Behavior-Driven Developement"-Tool written in python.
It is inspired by other ``BDD``-Tools like ``cucumber`` or ``lettuce``.

`[⬆] <#TOC>`__

Installation
------------

There are several ways to install ``radish`` on your computer:

`[⬆] <#TOC>`__

Missing dependencies
~~~~~~~~~~~~~~~~~~~~

``radish`` needs ``libxml`` to generated xunit files. So, if you haven't
already installed it:

::

    apt-get install libxml2 lixbml2-dev libxslt1-dev

On some computers I've seen the problem that ``zlib1g-dev`` was not
installed, which is used to compile lxml. It result in the error:

::

    /usr/bin/ld: cannot find -lz

You can fix it with:

::

    apt-get install zlib1g-develop

`[⬆] <#TOC>`__

Simple installation with pip
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is probably the simplest way to install ``radish``. Since the
``radish`` releases are hostet as well on
`pip <https://pypi.python.org/pypi/pip>`__ you can use the following
command to install ``radish``:

::

    pip install radish

*Note: On some systems you have to be root to install a package over
pip.*

`[⬆] <#TOC>`__

Manual installation from source
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you always want to be up to date with the newest commits you may want
to install ``radish`` directly from `source
code <https://github.com/timofurrer/radish>`__. Use the following
command sequence to clone the repository from github and install
``radish`` afterwards:

.. code:: bash

    git clone https://github.com/timofurrer/radish.git ~/radish
    cd ~/radish
    git submodule init
    git submodule update
    python setup.py install

*Note: On some systems you have to be root to install a package over
setuptools.*

`[⬆] <#TOC>`__

Update source installation
^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have once installation ``radish`` from source you might want to
update it from time to time. Change into the directory where you have
cloned ``radish`` into (default: ``~/radish``) and pull the newest
commit from github. When you've done this you need to re-install
``radish`` again. So, in summary:

.. code:: bash

    cd ~/radish
    git pull
    python setup.py install

*Note: On some systems you have to be root to install a package over
setuptools.*

`[⬆] <#TOC>`__

How to use?
-----------

.. code:: bash

    mkdir testprj
    cd testprj
    radish -c

.. code:: bash

    creating radish/
    creating radish/steps.py
    creating radish/terrain.py

.. code:: bash

    mkdir tests
    cat > tests/001-howto.feature <<EOF
    Feature: Provide a first test as example for using radish
      In order to be a good program, provide an example how to write a test.

      Scenario: Getting started using radish
        # Show the steps that need to be done to get testing with radish.

        Given I have radish version 0.01.15 installed

    EOF

.. code:: bash

    radish tests/001-howto.feature

.. code:: bash

    tests/001-howto.feature:7: error: no step definition found for 'Given I have radish version 0.01.15 installed'
    you might want to add the following to your steps.py:

    @step(u'I have radish version 0.01.15 installed')
    def I_have_radish_version_0_01_15_installed(step):
        assert False, "Not implemented yet"

add these 3 lines to radish/steps.py and run radish again:

.. code:: bash

    radish tests/001-howto.feature

1. Provide a first test as example for using radish # 001-howto.feature
   In order to be a good program, provide an example how to write a
   test.

   1. Getting started using radish

      1. Given I have radish version 0.01.15 installed AssertionError:
         Not implemented yet

1 features (0 passed, 1 failed) 1 scenarios (0 passed, 1 failed) 1 steps
(0 passed, 1 failed) (finished within 0 minutes and 0.00 seconds)

`[⬆] <#TOC>`__

Writing tests
-------------

Coming soon ...

`[⬆] <#TOC>`__

Contribution
------------

 Use virtualenv
~~~~~~~~~~~~~~~

I recommend you to develop ``radish`` in a virtualenv, because than you
can easily manage all the requirements.

.. code:: bash

    virtualenv radish-env --no-site-packages
    . radish-env/bin/activate
    pip install -r requirements.txt

More coming soon ...

`[⬆] <#TOC>`__

Infos
-----

The files which are currently in the testfiles-folder are from lettuce -
another TDD tool!

`[⬆] <#TOC>`__
