.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

caps.utils.bet.BET
==================


.. _caps.utils.bet.BET:


.. index:: BET

BET
---

.. currentmodule:: caps.utils.bet

.. autoclass:: BET
	:no-members:

Inputs
~~~~~~


[Mandatory]

+----------------------------------------------------+
| | **bet_threshold**: a float (mandatory)           |
| |     fractional intensity threshold               |
+----------------------------------------------------+
| | **generate_binary_mask**: a boolean (mandatory)  |
| |     create binary mask image                     |
+----------------------------------------------------+
| | **generate_mesh**: a boolean (mandatory)         |
| |     generate a vtk mesh brain surface            |
+----------------------------------------------------+
| | **generate_skull**: a boolean (mandatory)        |
| |     create skull image                           |
+----------------------------------------------------+
| | **input_file**: a file name (mandatory)          |
| |     input file to skull strip                    |
+----------------------------------------------------+
| | **use_4d_input**: a boolean (mandatory)          |
| |     apply to 4D fMRI data                        |
+----------------------------------------------------+

[Optional]


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

.. image:: ../schema/caps.utils.bet.BET.png
    :height: 400px
    :align: center

