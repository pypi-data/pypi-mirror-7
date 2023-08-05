.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

caps.diffusion_registration.reorientation.SecondOrderTensorReorientation
========================================================================


.. _caps.diffusion_registration.reorientation.SecondOrderTensorReorientation:


.. index:: SecondOrderTensorReorientation

SecondOrderTensorReorientation
------------------------------

.. currentmodule:: caps.diffusion_registration.reorientation

.. autoclass:: SecondOrderTensorReorientation
	:no-members:

Inputs
~~~~~~


[Mandatory]

+-------------------------------------------------------------+
| | **eigenvals_file**: a file name (mandatory)               |
| |     the second order tensor eigenvalues                   |
+-------------------------------------------------------------+
| | **eigenvecs_file**: a file name (mandatory)               |
| |     the second order tensor eigenvectors                  |
+-------------------------------------------------------------+
| | **local_affine_transform_file**: a file name (mandatory)  |
| |     the approximated local affine transformation          |
+-------------------------------------------------------------+

[Optional]

+--------------------------------------------------------------------+
| | **output_directory**: a directory name (optional)                |
| |     the output directory where the tensor model will be written  |
+--------------------------------------------------------------------+
| | **reorientation_strategy**: a legal value (optional)             |
| |     the reorientation strategy: ppd or fs                        |
+--------------------------------------------------------------------+
| | **reoriented_tensor_name**: a string (optional)                  |
| |     the name of the output reoriented tensor field               |
+--------------------------------------------------------------------+

Outputs
~~~~~~~

+--------------------------------------------+
| | **reoriented_tensor_file**: a file name  |
| |     the reoriented tensor field          |
+--------------------------------------------+
