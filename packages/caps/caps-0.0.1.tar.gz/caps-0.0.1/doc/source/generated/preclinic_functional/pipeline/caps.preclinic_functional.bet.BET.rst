.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

caps.preclinic_functional.bet.BET
=================================


.. _caps.preclinic_functional.bet.BET:


.. index:: BET

BET
---

.. currentmodule:: caps.preclinic_functional.bet

.. autoclass:: BET
	:no-members:

Inputs
~~~~~~


[Mandatory]

+--------------------------------------------+
| | **input_file**: a file name (mandatory)  |
| |     input file to skull strip            |
+--------------------------------------------+

[Optional]

+---------------------------------------------------+
| | **bet_threshold**: a float (optional)           |
| |     fractional intensity threshold              |
+---------------------------------------------------+
| | **generate_binary_mask**: a boolean (optional)  |
| |     create binary mask image                    |
+---------------------------------------------------+
| | **generate_mesh**: a boolean (optional)         |
| |     generate a vtk mesh brain surface           |
+---------------------------------------------------+
| | **generate_skull**: a boolean (optional)        |
| |     create skull image                          |
+---------------------------------------------------+
| | **use_4d_input**: a boolean (optional)          |
| |     apply to 4D fMRI data                       |
+---------------------------------------------------+

Outputs
~~~~~~~

+----------------------------------------------------------+
| | **bet_inskull_mask_file**: a file name                 |
| |     path/name of inskull mask (if generated)           |
+----------------------------------------------------------+
| | **bet_inskull_mesh_file**: a file name                 |
| |     path/name of inskull mesh outline (if generated)   |
+----------------------------------------------------------+
| | **bet_mask_file**: a file name                         |
| |     path/name of binary brain mask (if generated)      |
+----------------------------------------------------------+
| | **bet_meshfile**: a file name                          |
| |     path/name of vtk mesh file (if generated)          |
+----------------------------------------------------------+
| | **bet_out_file**: a file name                          |
| |     path/name of skullstripped file (if generated)     |
+----------------------------------------------------------+
| | **bet_outskin_mask_file**: a file name                 |
| |     path/name of outskin mask (if generated)           |
+----------------------------------------------------------+
| | **bet_outskin_mesh_file**: a file name                 |
| |     path/name of outskin mesh outline (if generated)   |
+----------------------------------------------------------+
| | **bet_outskull_mask_file**: a file name                |
| |     path/name of outskull mask (if generated)          |
+----------------------------------------------------------+
| | **bet_outskull_mesh_file**: a file name                |
| |     path/name of outskull mesh outline (if generated)  |
+----------------------------------------------------------+
| | **bet_skull_mask_file**: a file name                   |
| |     path/name of skull mask (if generated)             |
+----------------------------------------------------------+

Pipeline schema
~~~~~~~~~~~~~~~

.. image:: ../schema/caps.preclinic_functional.bet.BET.png
    :height: 400px
    :align: center

