.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

caps.diffusion_preproc.bet.dBET
===============================


.. _caps.diffusion_preproc.bet.dBET:


.. index:: dBET

dBET
----

.. currentmodule:: caps.diffusion_preproc.bet

.. autoclass:: dBET
	:no-members:

Inputs
~~~~~~


[Mandatory]

+----------------------------------------------------+
| | **bet_threshold**: a float (mandatory)           |
| |     fractional intensity threshold               |
+----------------------------------------------------+
| | **bvals**: a file name (mandatory)               |
| |     the the diffusion b-values                   |
+----------------------------------------------------+
| | **dw_image**: a file name (mandatory)            |
| |     an existing diffusion weighted image         |
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
| | **use_4d_input**: a boolean (mandatory)          |
| |     apply to 4D fMRI data                        |
+----------------------------------------------------+

[Optional]

+------------------------------------------------------------+
| | **specified_index_of_ref_image**: an integer (optional)  |
| |     index of the reference b=0 volume                    |
+------------------------------------------------------------+

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
| | **index_of_ref_image**: an integer                     |
| |     index of the reference b=0 volume                  |
+----------------------------------------------------------+
| | **outelements**: a legal value                         |
| |     list of selected values                            |
+----------------------------------------------------------+
| | **ref_image**: any value                               |
| |     selected value                                     |
+----------------------------------------------------------+
| | **splited_images**: a legal value or a file name       |
+----------------------------------------------------------+

Pipeline schema
~~~~~~~~~~~~~~~

.. image:: ../schema/caps.diffusion_preproc.bet.dBET.png
    :height: 400px
    :align: center

