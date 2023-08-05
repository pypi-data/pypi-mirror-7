.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

caps.diffusion_estimation.tensor_scalars.SecondOrderScalarParameters
====================================================================


.. _caps.diffusion_estimation.tensor_scalars.SecondOrderScalarParameters:


.. index:: SecondOrderScalarParameters

SecondOrderScalarParameters
---------------------------

.. currentmodule:: caps.diffusion_estimation.tensor_scalars

.. autoclass:: SecondOrderScalarParameters
	:no-members:

Inputs
~~~~~~


[Mandatory]

+--------------------------------------------------+
| | **eigenvalues_file**: a file name (mandatory)  |
| |     a second order tensor eigen values         |
+--------------------------------------------------+

[Optional]

+----------------------------------------------------------------------+
| | **cl_basename**: a string (optional)                               |
| |     the basename of the output linearity coefficients file         |
+----------------------------------------------------------------------+
| | **cp_basename**: a string (optional)                               |
| |     the basename of the output planarity coefficients file         |
+----------------------------------------------------------------------+
| | **cs_basename**: a string (optional)                               |
| |     the basename of the output sphericity coefficients file        |
+----------------------------------------------------------------------+
| | **fa_basename**: a string (optional)                               |
| |     the basename of the output fa file                             |
+----------------------------------------------------------------------+
| | **md_basename**: a string (optional)                               |
| |     the basename of the output md file                             |
+----------------------------------------------------------------------+
| | **output_directory**: a directory name (optional)                  |
| |     the output directory where the tensor scalars will be written  |
+----------------------------------------------------------------------+

Outputs
~~~~~~~

+----------------------------------------------------------------------+
| | **fractional_anisotropy_file**: a file name                        |
| |     the name of the output fa file                                 |
+----------------------------------------------------------------------+
| | **linearity_file**: a file name                                    |
| |     the name of the fie that contains the linerity coefficients    |
+----------------------------------------------------------------------+
| | **mean_diffusivity_file**: a file name                             |
| |     the name of the output md file                                 |
+----------------------------------------------------------------------+
| | **planarity_file**: a file name                                    |
| |     the name of the fie that contains the planarity coefficients   |
+----------------------------------------------------------------------+
| | **sphericity_file**: a file name                                   |
| |     the name of the fie that contains the sphericity coefficients  |
+----------------------------------------------------------------------+
