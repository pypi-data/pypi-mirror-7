.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

caps.diffusion_estimation.tensor_scalars.FourthOrderScalarParameters
====================================================================


.. _caps.diffusion_estimation.tensor_scalars.FourthOrderScalarParameters:


.. index:: FourthOrderScalarParameters

FourthOrderScalarParameters
---------------------------

.. currentmodule:: caps.diffusion_estimation.tensor_scalars

.. autoclass:: FourthOrderScalarParameters
	:no-members:

Inputs
~~~~~~


[Mandatory]

+---------------------------------------------+
| | **mask_file**: a file name (mandatory)    |
| |     a mask image                          |
+---------------------------------------------+
| | **tensor_file**: a file name (mandatory)  |
| |     a fourth order tensor model           |
+---------------------------------------------+

[Optional]

+----------------------------------------------------------------------+
| | **ga_basename**: a string (optional)                               |
| |     the basename of the output ga file                             |
+----------------------------------------------------------------------+
| | **md_basename**: a string (optional)                               |
| |     the basename of the output md file                             |
+----------------------------------------------------------------------+
| | **output_directory**: a directory name (optional)                  |
| |     the output directory where the tensor scalars will be written  |
+----------------------------------------------------------------------+

Outputs
~~~~~~~

+-------------------------------------------------+
| | **generalized_anisotropy_file**: a file name  |
| |     the name of the output fa file            |
+-------------------------------------------------+
| | **mean_diffusivity_file**: a file name        |
| |     the name of the output md file            |
+-------------------------------------------------+
