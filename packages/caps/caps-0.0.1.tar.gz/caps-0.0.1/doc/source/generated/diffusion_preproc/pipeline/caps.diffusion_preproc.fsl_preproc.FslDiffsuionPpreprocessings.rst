.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

caps.diffusion_preproc.fsl_preproc.FslDiffsuionPpreprocessings
==============================================================


.. _caps.diffusion_preproc.fsl_preproc.FslDiffsuionPpreprocessings:


.. index:: FslDiffsuionPpreprocessings

FslDiffsuionPpreprocessings
---------------------------

.. currentmodule:: caps.diffusion_preproc.fsl_preproc

.. autoclass:: FslDiffsuionPpreprocessings
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
| | **bvecs**: a file name (mandatory)               |
| |     the diffusion b-vectors                      |
+----------------------------------------------------+
| | **complex_phase_file**: a file name (mandatory)  |
| |     complex phase input volume                   |
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
| | **magnitude_file**: a file name (mandatory)      |
| |     file containing magnitude image              |
+----------------------------------------------------+
| | **phase_file**: a file name (mandatory)          |
| |     raw phase file                               |
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
| | **affine_transformations**: a legal value              |
| |     path of the calculated rigid transformations       |
+----------------------------------------------------------+
| | **bet_inskull_mask_file**: a file name                 |
| |     path/name of inskull mask (if generated)           |
+----------------------------------------------------------+
| | **bet_inskull_mesh_file**: a file name                 |
| |     path/name of inskull mesh outline (if generated)   |
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
| | **corrected_file**: any value                          |
+----------------------------------------------------------+
| | **eddy_corrected_files**: a file name                  |
+----------------------------------------------------------+
| | **index_of_ref_image**: an integer                     |
| |     index of the reference b=0 volume                  |
+----------------------------------------------------------+
| | **motion_corrected_image**: a file name                |
+----------------------------------------------------------+
| | **outelements**: a legal value                         |
| |     list of selected values                            |
+----------------------------------------------------------+
| | **reoriented_bvecs**: any value                        |
+----------------------------------------------------------+
| | **rigid_transformations**: a legal value               |
| |     path of the calculated rigid transformations       |
+----------------------------------------------------------+
| | **susceptibility_corrected_file**: a file name         |
| |     unwarped file                                      |
+----------------------------------------------------------+
| | **unwrapped_phase_file**: a file name                  |
| |     unwrapped phase file                               |
+----------------------------------------------------------+

Pipeline schema
~~~~~~~~~~~~~~~

.. image:: ../schema/caps.diffusion_preproc.fsl_preproc.FslDiffsuionPpreprocessings.png
    :height: 400px
    :align: center

