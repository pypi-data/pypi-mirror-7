.. BatchOpenMPI documentation master file, created by
   sphinx-quickstart on Thu Dec  3 11:58:56 2009.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to BatchOpenMPI's documentation!
========================================

batchOpenMPI offers easy to get started with parallelization for Python.
batchOpenMPI is built on top of mpi4py which makes use of openMPI.
batchOpenMPI uses a fixed typology of having 1 master process which hand out jobs and runs the main code.
The other processes are workers, which complete the jobs handed out by the master.
Load balancing over the workers and other features are implemented, as the these docs will show examples for.

Contents:

.. toctree::
   :maxdepth: 1
   
   gettingStarted
   examples

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
