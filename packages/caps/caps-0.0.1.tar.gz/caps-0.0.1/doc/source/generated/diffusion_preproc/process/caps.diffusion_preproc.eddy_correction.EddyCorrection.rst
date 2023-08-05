.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

caps.diffusion_preproc.eddy_correction.EddyCorrection
=====================================================


.. _caps.diffusion_preproc.eddy_correction.EddyCorrection:


.. index:: EddyCorrection

EddyCorrection
--------------

.. currentmodule:: caps.diffusion_preproc.eddy_correction

.. autoclass:: EddyCorrection
	:no-members:

Inputs
~~~~~~


[Mandatory]

+------------------------------------------------+
| | **in_files**: a legal value (mandatory)      |
| |     a serie of images to correct             |
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
| | **affine_transformations**: a legal value         |
| |     path of the calculated rigid transformations  |
+-----------------------------------------------------+
| | **eddy_corrected_files**: a legal value           |
| |     path of the registered images                 |
+-----------------------------------------------------+
