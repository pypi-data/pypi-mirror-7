.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

caps.diffusion_estimation.tensor_estimation.LSTensorEstimation
==============================================================


.. _caps.diffusion_estimation.tensor_estimation.LSTensorEstimation:


.. index:: LSTensorEstimation

LSTensorEstimation
------------------

.. currentmodule:: caps.diffusion_estimation.tensor_estimation

.. autoclass:: LSTensorEstimation
	:no-members:

Inputs
~~~~~~


[Mandatory]

+---------------------------------------------+
| | **bvals_file**: a file name (mandatory)   |
| |     the the diffusion b-values            |
+---------------------------------------------+
| | **bvecs_file**: a file name (mandatory)   |
| |     the the diffusion b-vectors           |
+---------------------------------------------+
| | **dwi_file**: a file name (mandatory)     |
| |     an existing diffusion weighted image  |
+---------------------------------------------+
| | **mask_file**: a file name (mandatory)    |
| |     a mask image                          |
+---------------------------------------------+
| | **model_order**: an integer (mandatory)   |
| |     the estimated model order (even)      |
+---------------------------------------------+

[Optional]

+--------------------------------------------------------------------+
| | **estimate_odf**: a boolean (optional)                           |
| |     estimate the odf                                             |
+--------------------------------------------------------------------+
| | **model_name**: a string (optional)                              |
| |     the name of the output tensor model file                     |
+--------------------------------------------------------------------+
| | **output_directory**: a directory name (optional)                |
| |     the output directory where the tensor model will be written  |
+--------------------------------------------------------------------+

Outputs
~~~~~~~

+-----------------------------------------------------------------+
| | **tensor_file**: a file name                                  |
| |     the result file containing the tensor model coefficients  |
+-----------------------------------------------------------------+
