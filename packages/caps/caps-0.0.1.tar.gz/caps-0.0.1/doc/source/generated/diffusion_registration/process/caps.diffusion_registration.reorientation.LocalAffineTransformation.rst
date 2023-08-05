.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

caps.diffusion_registration.reorientation.LocalAffineTransformation
===================================================================


.. _caps.diffusion_registration.reorientation.LocalAffineTransformation:


.. index:: LocalAffineTransformation

LocalAffineTransformation
-------------------------

.. currentmodule:: caps.diffusion_registration.reorientation

.. autoclass:: LocalAffineTransformation
	:no-members:

Inputs
~~~~~~


[Mandatory]

+--------------------------------------------+
| | **field_file**: a file name (mandatory)  |
| |     the deformation field (dx, dy, dz)   |
+--------------------------------------------+

[Optional]

+--------------------------------------------------------------------+
| | **local_affine_transform_name**: a string (optional)             |
| |     the name of the output local affine transform file           |
+--------------------------------------------------------------------+
| | **output_directory**: a directory name (optional)                |
| |     the output directory where the tensor model will be written  |
+--------------------------------------------------------------------+

Outputs
~~~~~~~

+-----------------------------------------------------+
| | **local_affine_transform_file**: a file name      |
| |     the approximated local affine transformation  |
+-----------------------------------------------------+
