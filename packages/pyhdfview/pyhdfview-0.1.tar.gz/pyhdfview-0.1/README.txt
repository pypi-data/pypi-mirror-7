PyHdfView
=========

A simple command line viewer for HDF5 files.

*NOTE:* This is still an early protype.


Usage
=====

List groups of a database:

.. code-block:: bash

   $ hv ../mosaik-hdf5/tests/data/testdb.hdf5
   List ../mosaik-hdf5/tests/data/testdb.hdf5:/
   • Relations

List sub-groups of a group:

.. code-block:: bash

   $ hv ../mosaik-hdf5/tests/data/testdb.hdf5:/Relations
   List ../mosaik-hdf5/tests/data/testdb.hdf5:/Relations
   • DB-0.hdf5db
   • Sim-0.0.0
   • Sim-1.0.0
   • Sim-1.0.1

Print dataset:

.. code-block:: bash

   $ hv ../mosaik-hdf5/tests/data/testdb.hdf5:/Relations/Sim-0.0.0
   Dataset ../mosaik-hdf5/tests/data/testdb.hdf5:/Relations/Sim-0.0.0
   [b'DB-0.hdf5db' b'Sim-1.0.0' b'Sim-1.0.1']

Print attributes:

.. code-block:: bash

   $ hv attrs ../mosaik-hdf5/tests/data/testdb.hdf5:/Relations/Sim-0.0.0
   Attributes of ../mosaik-hdf5/tests/data/testdb.hdf5:/Relations/Sim-0.0.0
   • spam: eggs
   •  foo: bar
