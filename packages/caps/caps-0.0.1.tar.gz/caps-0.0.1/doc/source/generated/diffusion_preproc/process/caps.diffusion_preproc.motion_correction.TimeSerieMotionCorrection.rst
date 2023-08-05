.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

caps.diffusion_preproc.motion_correction.TimeSerieMotionCorrection
==================================================================


.. _caps.diffusion_preproc.motion_correction.TimeSerieMotionCorrection:


.. index:: TimeSerieMotionCorrection

TimeSerieMotionCorrection
-------------------------

.. currentmodule:: caps.diffusion_preproc.motion_correction

.. autoclass:: TimeSerieMotionCorrection
	:no-members:

Inputs
~~~~~~


[Mandatory]

+------------------------------------------------+
| | **bvecs**: a file name (mandatory)           |
| |     the diffusion b-vectors                  |
+------------------------------------------------+
| | **in_files**: a legal value (mandatory)      |
| |     a serie of images to registered          |
+------------------------------------------------+
| | **reference_file**: a file name (mandatory)  |
| |     the reference image                      |
+------------------------------------------------+

[Optional]

+------------------------------------------------------+
| | **output_directory**: a directory name (optional)  |
| |     the output directory                           |
+------------------------------------------------------+

Outputs
~~~~~~~

+-----------------------------------------------------+
| | **motion_corrected_files**: a legal value         |
| |     path of the registered images                 |
+-----------------------------------------------------+
| | **reoriented_bvecs**: a file name                 |
| |     the reoriented diffusion b-vectors            |
+-----------------------------------------------------+
| | **rigid_transformations**: a legal value          |
| |     path of the calculated rigid transformations  |
+-----------------------------------------------------+
