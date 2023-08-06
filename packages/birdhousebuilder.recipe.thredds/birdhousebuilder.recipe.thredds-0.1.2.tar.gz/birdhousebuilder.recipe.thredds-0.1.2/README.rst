*******************************
birdhousebuilder.recipe.thredds
*******************************

.. contents::

Introduction
************

``birdhousebuilder.recipe.thredds`` is a `Buildout`_ recipe to install and configure `Thredds`_ server with `Anaconda`_.

.. _`Buildout`: http://buildout.org/
.. _`Anaconda`: http://www.continuum.io/
.. _`Supervisor`: http://supervisord.org/
.. _`Thredds`: http://www.unidata.ucar.edu/software/thredds/current/tds/TDS.html


Usage
*****

The recipe requires that Anaconda is already installed. It assumes that Anaconda is installed at the default location in your home directory ``~/anaconda``. Otherwise you need to set the Buildout option ``anaconda-home`` to the correct location.

It installs the ``thredds`` and ``apache-tomcat`` package from a conda channel and setups Tomcat with Thredds. It deploys a `Supervisor`_ configuration for Tomcat in ``~/anaconda/etc/supervisor/conf.d/tomcat.conf``. Supervisor can be started with ``~/anaconda/etc/init.d/supervisord start``.

The recipe depends on ``birdhousebuilder.recipe.conda``, ``birdhousebuilder.recipe.supervisor`` and ``birdhousebuilder.recipe.tomcat``.

Supported options
=================

This recipe supports the following options:

``anaconda-home``
   Buildout option with the root folder of the Anaconda installation. Default: ``$HOME/anaconda``.

``data_root``
  Root Path of data files (NetCDF) for Thredds.

Example usage
=============

The following example ``buildout.cfg`` installs Thredds with Anaconda and given ``data_root`` directory::

  [buildout]
  parts = thredds

  anaconda-home = /home/myself/anaconda

  [thredds]
  recipe = birdhousebuilder.recipe.thredds
  data_root = ${buildout:anaconda-home}/var/lib/thredds/data_root


