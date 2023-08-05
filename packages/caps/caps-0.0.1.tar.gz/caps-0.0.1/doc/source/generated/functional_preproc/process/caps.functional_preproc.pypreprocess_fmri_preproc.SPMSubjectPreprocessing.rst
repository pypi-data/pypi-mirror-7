.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

caps.functional_preproc.pypreprocess_fmri_preproc.SPMSubjectPreprocessing
=========================================================================


.. _caps.functional_preproc.pypreprocess_fmri_preproc.SPMSubjectPreprocessing:


.. index:: SPMSubjectPreprocessing

SPMSubjectPreprocessing
-----------------------

.. currentmodule:: caps.functional_preproc.pypreprocess_fmri_preproc

.. autoclass:: SPMSubjectPreprocessing
	:no-members:

Inputs
~~~~~~


[Mandatory]

+--------------------------------------------------------------------------+
| | **anat_file**: a file name (mandatory)                                 |
| |     Path to the anatomical image                                       |
+--------------------------------------------------------------------------+
| | **func_file**: a file name or a legal value or an implementor of, or   |
| |     can be adapted to implement, _Undefined or None (mandatory)        |
| |     Path to the functional image(s)                                    |
+--------------------------------------------------------------------------+
| | **fwhm**: a legal value or a float or an implementor of, or can be     |
| |     adapted to implement, _Undefined or None (mandatory)               |
| |     FWHM for smoothing the functional data. If normalize is set, then  |
| |     this parameter is based to spm.Normalize, else spm.Smooth is used  |
| |     to explicitly smooth the functional data.                          |
+--------------------------------------------------------------------------+
| | **repetition_time**: a float (mandatory)                               |
| |     The repetition time of the functional iamge acquisition sequence.  |
+--------------------------------------------------------------------------+
| | **slice_order**: a legal value (mandatory)                             |
| |     The acquistion order of each slice of the functional iamge.        |
+--------------------------------------------------------------------------+

[Optional]

+--------------------------------------------------------------------------+
| | **coreg_anat_to_func**: a boolean (optional)                           |
| |     If set, then functional data will be the reference during          |
| |     coregistration. By default the anatomical data if the reference,   |
| |     to ensure a precise registration (since anatomical data has finer  |
| |     resolution)                                                        |
+--------------------------------------------------------------------------+
| | **coregister**: a boolean (optional)                                   |
| |     If set, the functional and anatomical images will be               |
| |     corregistered. If this not set, and anatomical image is defined,   |
| |     it is assumed that functional and anatomical images have already   |
| |     been coregistered.                                                 |
+--------------------------------------------------------------------------+
| | **normalize**: a boolean (optional)                                    |
| |     If set, then the subject_data (functional and anatomical) will be  |
| |     warped into MNI space                                              |
+--------------------------------------------------------------------------+
| | **output_directory**: a directory name (optional)                      |
| |     Path to the output directory                                       |
+--------------------------------------------------------------------------+
| | **realign**: a boolean (optional)                                      |
| |     If set, then the functional data will be realigned to correct for  |
| |     head-motion.                                                       |
+--------------------------------------------------------------------------+
| | **segment**: a boolean (optional)                                      |
| |     If set, then the subject's anatomical image will be segmented to   |
| |     produce GM, WM, and CSF compartments (useful for both indirect     |
| |     normalization (intra-subject) or DARTEL (inter-subject) alike      |
+--------------------------------------------------------------------------+
| | **slice_time**: a boolean (optional)                                   |
| |     If set, then the functional data will be correction for slice      |
| |     timing distortions.                                                |
+--------------------------------------------------------------------------+
| | **use_smart_caching**: a boolean (optional)                            |
| |     If set, then use nipype smart-caching.                             |
+--------------------------------------------------------------------------+

Outputs
~~~~~~~

+---------------------------------------------------------------------------+
| | **coregister_file**: a file name or a legal value or an implementor     |
| |     of, or can be adapted to implement, _Undefined or None              |
| |     The coregister image(s).                                            |
+---------------------------------------------------------------------------+
| | **mean_file**: a file name or a legal value or an implementor of, or    |
| |     can be adapted to implement, _Undefined or None                     |
| |     The functional realigned mean image.                                |
+---------------------------------------------------------------------------+
| | **normalize_anat_file**: a file name or a legal value or an             |
| |     implementor of, or can be adapted to implement, _Undefined or None  |
| |     The normalize file(s)                                               |
+---------------------------------------------------------------------------+
| | **normalize_func_file**: a file name or a legal value or an             |
| |     implementor of, or can be adapted to implement, _Undefined or None  |
| |     The normalize file(s)                                               |
+---------------------------------------------------------------------------+
| | **realign_file**: a file name or a legal value or an implementor of,    |
| |     or can be adapted to implement, _Undefined or None                  |
| |     The functional realigned image(s) (head-motion correction).         |
+---------------------------------------------------------------------------+
| | **segment_file**: a file name or a legal value or an implementor of,    |
| |     or can be adapted to implement, _Undefined or None                  |
+---------------------------------------------------------------------------+
| | **slice_time_corrected_file**: a file name or a legal value or an       |
| |     implementor of, or can be adapted to implement, _Undefined or None  |
| |     The functional slice time corrected image(s).                       |
+---------------------------------------------------------------------------+
| | **smooth_normalize_func_file**: a file name or a legal value or an      |
| |     implementor of, or can be adapted to implement, _Undefined or None  |
| |     The normalize and smoothed functional file(s)                       |
+---------------------------------------------------------------------------+
| | **transformation_file**: a file name or a legal value or an             |
| |     implementor of, or can be adapted to implement, _Undefined or None  |
| |     The functional realigned transformation parameters.                 |
+---------------------------------------------------------------------------+
