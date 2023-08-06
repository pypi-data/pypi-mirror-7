.. _buildout: http://www.buildout.org/
.. _pip: http://www.pip-installer.org/
.. _virtualenv: http://www.virtualenv.org/
.. _Gestus: https://github.com/sveetch/Gestus
.. _nap: https://github.com/kimmobrunfeldt/nap

**Gestus-client** is the REST client to retrieve and push data on a `Gestus`_ app. It is currently only working with eggs installation like in a `buildout`_ project.

Install
=======

Require
*******

* `nap`_ >= 1.0.0;
* pkginfo >= 1.2b1;
* argparse == 1.2.1;
* argcomplete == 0.8.0;
* argh == 0.24.1;

Also this client rely on ``pkg_resources`` that comes from Distribute, but Distribute is not registered in required packages in the ``setup.py`` because it is embedded within PIP that is ofent allready installed on your system. So if the script complain about to import ``pkg_resources``, you will have to install PIP or Distribute.

PIP version
-----------

`nap`_ requires ``PIP >= 1.4``. You will have to update it if you have an exception like this during installation : ::

    AttributeError: 'NoneType' object has no attribute 'skip_requirements_regex'
    An error occurred when trying to install nap 1.0.1. Look above this message for any errors that were output by easy_install.
    While:
    Installing eggedpy.
    Getting distribution for 'nap>=1.0.0'.
    Error: Couldn't install: nap 1.0.1

The simpliest method to resolve this is to simply update `pip`_ in your virtual environment to the last version : ::

    pip install --upgrade pip

Usage
=====

The client can register a new website environment or update an allready existing environment.

During the register or update action, if the eggs directory is given it will be scanned to search for installed eggs, a list of finded eggs will be sended to the service.

Website environment's datas can be setted either from the command line arguments or from a config file. If a config file is used it will be used to fill the default datas to send and you can overrides them with the command line arguments. 

So if in the Config file you setted the ``user`` option to ``ping`` and set this option to ``pong`` in the command line args, the used value will be ``pong``.


Config
******

The client can be used directly, but you should create a ``gestus.cfg`` file in your project to avoid to put arguments on the command line.

The file format is like ``*.INI`` file, here is a full example : ::

    [Gestus]
    user = your username
    password = your password
    host = service url
    name = website name
    url = environment url
    env = environment name
    eggs = eggs directory
    server = website hostname

Available options are :

* **user**: the username to connect to the service;
* **password**: the password to connect to the service;
* **host**: the service's url (http/https);
* **name**: the website project name;
* **url**: the environment url where the project is attempted to be published;
* **env**: the environment kind name (``integration`` or ``production``);
* **eggs**: the path to eggs directory to scan;
* **server**: the website hostname;

There are all optionnal to register a new environment. But to update an allready existing environment you will need at least two additional options :

* website_id = the website's ID as it has been registered on the Gestus service;
* environment_id = the environment's ID as it has been registered on the Gestus service;

You don't really have to take care about these optionnal options because they will be automatically retrieved and stored on the first register.

Config saving
-------------

Note that a Config file is automatically saved at the end of a register or update action, you can disable this using the ``passive`` argument : ::

    gestus --passive

Else the default behavior is to save a ``gestus.cfg`` file in the current directory, you can set another filename and path with ``config`` argument : ::

    gestus --config /home/foo/bar/my-gestus-config.cfg

So if you have multiple site to support in a single project, allways use a specific config file for each site.

Register a new website environment
==================================

This will only register a new environment, you can't update an allready existing website environment datas from this command.

    gestus register

If the website environment allready exists, the register command will get its datas and saving in a config file, then it will send again the egg list, this is the only thing that can be updated from this command.

If it does not exist, it will create it, then send the egg list and save returned datas in the config file.

Warning : You have to maintain a clean install for your eggs, the Gestus client will ensure to allways use the last egg version of a same package, so if you installed a last version for some tests and got back to a previous one for any reason, the client will even though register the last one because it don't know about the one you effectively use. So take care to this and clean your installed eggs when you have made some package testing in your environment.
