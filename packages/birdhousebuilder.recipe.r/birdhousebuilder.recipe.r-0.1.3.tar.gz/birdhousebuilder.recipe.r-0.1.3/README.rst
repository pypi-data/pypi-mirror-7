*************************
birdhousebuilder.recipe.r
*************************

.. contents::

Introduction
************

``birdhousebuilder.recipe.r`` is a `Buildout`_ recipe to install `R Project`_ packages with `Anaconda`_.

.. _`Buildout`: http://buildout.org/
.. _`Anaconda`: http://continuum.io/
.. _`R Project`: http://www.r-project.org/

Usage
*****

The recipe requires that Anaconda is already installed. It assumes that Anaconda is installed at the default location in your home directory ``~/anaconda``. Otherwise you need to set the Buildout option ``anaconda-home`` to the correct location.

It installs the ``r`` package from a conda channel with additional packages from a given ``R`` repository. ``R`` will then be available in Anaconda ``~/anaconda/bin/R``.

The recipe depends on ``birdhousebuilder.recipe.conda``.

Supported options
=================

The recipe supports the following options:

``anaconda-home``
   Buildout option with the root folder of the Anaconda installation. Default: ``$HOME/anaconda``.

``repo``
   `R Project`_ repository with ``R`` packages.

``pkgs``
   List of ``R`` packages which should be installed (space separated).


Example usage
=============

Example usage in your ``buildout.cfg`` to install ``R`` with Anaconda and additional ``R`` packages (``sp``, ``raster``, ``ncdf``) from a ``R`` repository::

  [buildout]
  parts = r_pkgs

  anaconda-home = /home/myself/anaconda

  [r_pkgs]
  recipe = birdhousebuilder.recipe.r
  repo = http://ftp5.gwdg.de/pub/misc/cran
  pkgs = sp raster ncdf

