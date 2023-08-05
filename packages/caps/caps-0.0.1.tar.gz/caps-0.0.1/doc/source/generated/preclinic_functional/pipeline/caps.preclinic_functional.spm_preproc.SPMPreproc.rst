.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

caps.preclinic_functional.spm_preproc.SPMPreproc
================================================


.. _caps.preclinic_functional.spm_preproc.SPMPreproc:


.. index:: SPMPreproc

SPMPreproc
----------

.. currentmodule:: caps.preclinic_functional.spm_preproc

.. autoclass:: SPMPreproc
	:no-members:

Inputs
~~~~~~


[Mandatory]

+---------------------------------------------------------------+
| | **register_to_mean**: a boolean (mandatory)                 |
| |     Indicate whether realignment is done to the mean image  |
+---------------------------------------------------------------+

[Optional]

+---------------------------------------------------------+
| | **bet_threshold**: a float (optional)                 |
| |     fractional intensity threshold                    |
+---------------------------------------------------------+
| | **fwhm**: a legal value (optional)                    |
| |     gaussian smoothing kernel width (mm)              |
+---------------------------------------------------------+
| | **generate_binary_mask**: a boolean (optional)        |
| |     create binary mask image                          |
+---------------------------------------------------------+
| | **generate_mesh**: a boolean (optional)               |
| |     generate a vtk mesh brain surface                 |
+---------------------------------------------------------+
| | **generate_skull**: a boolean (optional)              |
| |     create skull image                                |
+---------------------------------------------------------+
| | **smooth_fwhm**: a legal value or a float (optional)  |
| |     3-list of fwhm for each dimension (opt)           |
+---------------------------------------------------------+
| | **use_4d_input**: a boolean (optional)                |
| |     apply to 4D fMRI data                             |
+---------------------------------------------------------+

Outputs
~~~~~~~

+----------------------------------------------------------+
| | **acquisition_time**: a float                          |
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
| | **coregistered_image**: a file name                    |
+----------------------------------------------------------+
| | **normalization_parameter**: any value                 |
+----------------------------------------------------------+
| | **normalized_func_image**: any value                   |
+----------------------------------------------------------+
| | **normalized_struct_image**: any value                 |
+----------------------------------------------------------+
| | **number_of_slices**: an integer                       |
+----------------------------------------------------------+
| | **realigned_time_series_image**: a file name           |
+----------------------------------------------------------+
| | **reference_mean_image**: a file name                  |
+----------------------------------------------------------+
| | **repetition_time**: a float                           |
+----------------------------------------------------------+
| | **slice_times**: a legal value                         |
+----------------------------------------------------------+
| | **smoothed_image**: a file name                        |
+----------------------------------------------------------+
| | **time_corrected_fmri_image**: a file name             |
+----------------------------------------------------------+

Pipeline schema
~~~~~~~~~~~~~~~

.. image:: ../schema/caps.preclinic_functional.spm_preproc.SPMPreproc.png
    :height: 400px
    :align: center

