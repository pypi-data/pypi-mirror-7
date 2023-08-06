*******************************
birdhousebuilder.recipe.mongodb
*******************************

.. contents::

Introduction
************

``birdhousebuilder.recipe.mongodb`` is a `Buildout`_ recipe to install and setup `MongoDB`_ with `Anaconda`_.

.. _`Buildout`: http://buildout.org/
.. _`Anaconda`: http://continuum.io/
.. _`MongoDB`: http://www.mongodb.org/
.. _`Supervisor`: http://supervisord.org/

Usage
*****

The recipe requires that Anaconda is already installed. It assumes that Anaconda is installed at the default location in your home directory ``~/anaconda``. Otherwise you need to set the Buildout option ``anaconda-home`` to the correct location.

It installs the ``mongodb`` package from a conda channel and setups a `MongoDB`_ database in ``~/anaconda/var/lib/mongodb``. It deploys as `Supervisor`_ configuration for MongoDB in ``~/anaconda/etc/supervisor/conf.d/mongodb.conf``. MongoDB can be started with ``~/anaconda/etc/init.d/mongodb start``.

The recipe depends on ``birdhousebuilder.recipe.conda`` and ``birdhousebuilder.recipe.supervisor``.

Supported options
=================

The recipe supports the following options:

``anaconda-home``
   Buildout option with the root folder of the Anaconda installation. Default: ``$HOME/anaconda``.


Example usage
=============

The following example ``buildout.cfg`` installs MongoDB with Anaconda::

  [buildout]
  parts = myapp_mongodb

  anaconda-home = /home/myself/anaconda

  [myapp_mongodb]
  recipe = birdhousebuilder.recipe.mongodb


