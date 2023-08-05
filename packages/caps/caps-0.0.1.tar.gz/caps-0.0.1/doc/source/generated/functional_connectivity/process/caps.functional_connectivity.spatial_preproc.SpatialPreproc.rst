.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

caps.functional_connectivity.spatial_preproc.SpatialPreproc
===========================================================


.. _caps.functional_connectivity.spatial_preproc.SpatialPreproc:


.. index:: SpatialPreproc

SpatialPreproc
--------------

.. currentmodule:: caps.functional_connectivity.spatial_preproc

.. autoclass:: SpatialPreproc
	:no-members:

Inputs
~~~~~~


[Mandatory]

+---------------------------------------------------------------------+
| | **anatomical_paths**: a legal value (mandatory)                   |
| |     paths to all subjects anatomical directories                  |
+---------------------------------------------------------------------+
| | **functional_paths**: a legal value (mandatory)                   |
| |     paths to all subjects functional directories                  |
+---------------------------------------------------------------------+
| | **raw_anatomical_images**: a legal value (mandatory)              |
| |     the anatomical files to spatially preprocess                  |
+---------------------------------------------------------------------+
| | **raw_anatomical_prefix**: a string (mandatory)                   |
| |     the prefix of the raw anatomical images                       |
+---------------------------------------------------------------------+
| | **raw_functional_images**: a legal value (mandatory)              |
| |     the functional files to spatially preprocess                  |
+---------------------------------------------------------------------+
| | **raw_functional_prefixes**: a legal value (mandatory)            |
| |     the prefixes of the raw functional imagesassociated to the    |
| |     sessions to include                                           |
+---------------------------------------------------------------------+
| | **steps**: a legal value (mandatory)                              |
| |     spatial preprocessing steps. Default to all steps:            |
| |     ['segmentation','slicetiming',                                |
| |     'realignment','coregistration','normalization', 'smoothing']  |
+---------------------------------------------------------------------+
| | **t_r**: a float (mandatory)                                      |
| |     Repetition time (seconds) [2]                                 |
+---------------------------------------------------------------------+

[Optional]

+--------------------------------------------------------------------------+
| | **nessions**: an integer (optional)                                    |
| |     Number of sessions                                                 |
+--------------------------------------------------------------------------+
| | **nsubjects**: an integer (optional)                                   |
| |     Number of subjects                                                 |
+--------------------------------------------------------------------------+
| | **slice_order**: any value (optional)                                  |
| |     (option for slicetiming step) acquisition order (vector of         |
| |     indexes; 1=first slice in image)                                   |
+--------------------------------------------------------------------------+
| | **smoothing_fwhm**: an integer (optional)                              |
| |     Smoothing factor (mm) [8]                                          |
+--------------------------------------------------------------------------+
| | **template_functional**: a file name (optional)                        |
| |     functional template file for normalization [spm/template/EPI.nii]  |
+--------------------------------------------------------------------------+
| | **template_structural**: a file name (optional)                        |
| |     anatomical template file for approximate coregistration            |
| |     [spm/template/T1.nii]                                              |
+--------------------------------------------------------------------------+
| | **voxel_size**: an integer (optional)                                  |
| |     target voxel size (mm) [2]                                         |
+--------------------------------------------------------------------------+

Outputs
~~~~~~~

+---------------------------------------------------------------------------+
| | **CSF_masks**: a legal value                                            |
| |     the spatially preprocessed CSF masks, output ofsegmentation step    |
+---------------------------------------------------------------------------+
| | **Grey_masks**: a legal value                                           |
| |     the spatially preprocessed Grey masks, output ofsegmentation step   |
+---------------------------------------------------------------------------+
| | **White_masks**: a legal value                                          |
| |     the spatially preprocessed White masks, output ofsegmentation step  |
+---------------------------------------------------------------------------+
| | **conn_batch**: a legal value                                           |
| |     the generated conn batch                                            |
+---------------------------------------------------------------------------+
| | **normalized**: an integer                                              |
| |     1/0 are the spatially preprocessed images normalized or not         |
+---------------------------------------------------------------------------+
| | **realignment_covariate_files**: a legal value                          |
| |     the realignment parameters files output ofrealignment step          |
+---------------------------------------------------------------------------+
| | **realignment_covariate_name**: a legal value                           |
| |     name of the realignment covariate                                   |
+---------------------------------------------------------------------------+
| | **single_condition_duration**: a legal value                            |
| |     duration inf for the single condition                               |
+---------------------------------------------------------------------------+
| | **single_condition_name**: a legal value                                |
| |     one single condition named 'Session' set to model the entire        |
| |     session data                                                        |
+---------------------------------------------------------------------------+
| | **single_condition_onset**: a legal value                               |
| |     onset 0.0 for the single condition                                  |
+---------------------------------------------------------------------------+
| | **spreproc_anatomical_images**: a legal value                           |
| |     spatially preprocessed anatomical images                            |
+---------------------------------------------------------------------------+
| | **spreproc_functional_images**: a legal value                           |
| |     spatially preprocessed functionale images                           |
+---------------------------------------------------------------------------+
