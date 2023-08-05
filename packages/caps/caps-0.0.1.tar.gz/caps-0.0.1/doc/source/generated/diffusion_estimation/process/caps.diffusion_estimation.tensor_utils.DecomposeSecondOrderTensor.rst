.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

caps.diffusion_estimation.tensor_utils.DecomposeSecondOrderTensor
=================================================================


.. _caps.diffusion_estimation.tensor_utils.DecomposeSecondOrderTensor:


.. index:: DecomposeSecondOrderTensor

DecomposeSecondOrderTensor
--------------------------

.. currentmodule:: caps.diffusion_estimation.tensor_utils

.. autoclass:: DecomposeSecondOrderTensor
	:no-members:

Inputs
~~~~~~


[Mandatory]

+---------------------------------------------+
| | **tensor_file**: a file name (mandatory)  |
| |     a second order tensor model           |
+---------------------------------------------+

[Optional]

+---------------------------------------------------------------------------+
| | **eigenvals_basename**: a string (optional)                             |
| |     the basename of the output eigen values file                        |
+---------------------------------------------------------------------------+
| | **eigenvecs_basename**: a string (optional)                             |
| |     the basename of the output eigen vectors file                       |
+---------------------------------------------------------------------------+
| | **number_of_workers**: an integer (optional)                            |
| |     the number of CPUs to use during the execution                      |
+---------------------------------------------------------------------------+
| | **output_directory**: a directory name (optional)                       |
| |     the output directory where the tensor eigenvalues and eigenvectors  |
| |     will be written                                                     |
+---------------------------------------------------------------------------+

Outputs
~~~~~~~

+--------------------------------------------------+
| | **eigen_values_file**: a file name             |
| |     the name of the output eigen values file   |
+--------------------------------------------------+
| | **eigen_vectors_file**: a file name            |
| |     the name of the output eigen vectors file  |
+--------------------------------------------------+
