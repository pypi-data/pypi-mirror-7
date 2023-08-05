.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

caps.diffusion_estimation.py_tensor_estimation.FourthOrderTensorEstimation
==========================================================================


.. _caps.diffusion_estimation.py_tensor_estimation.FourthOrderTensorEstimation:


.. index:: FourthOrderTensorEstimation

FourthOrderTensorEstimation
---------------------------

.. currentmodule:: caps.diffusion_estimation.py_tensor_estimation

.. autoclass:: FourthOrderTensorEstimation
	:no-members:

Inputs
~~~~~~


[Mandatory]

+------------------------------------------------+
| | **bvals_file**: a file name (mandatory)      |
| |     the the diffusion b-values               |
+------------------------------------------------+
| | **bvecs_file**: a file name (mandatory)      |
| |     the the diffusion b-vectors              |
+------------------------------------------------+
| | **dwi_file**: a file name (mandatory)        |
| |     an existing diffusion weighted image     |
+------------------------------------------------+
| | **mask_file**: a file name (mandatory)       |
| |     a mask image                             |
+------------------------------------------------+
| | **reference_file**: a file name (mandatory)  |
| |     the referecne b=0 image                  |
+------------------------------------------------+

[Optional]

+-------------------------------------------+
| | **estimate_odf**: a boolean (optional)  |
| |     estimate the odf                    |
+-------------------------------------------+

Outputs
~~~~~~~

+-------------------------------------------------+
| | **generalized_anisotropy_file**: a file name  |
| |     the name of the output fa file            |
+-------------------------------------------------+
| | **mean_diffusivity_file**: a file name        |
| |     the name of the output md file            |
+-------------------------------------------------+
| | **tensor_file**: any value                    |
+-------------------------------------------------+

Pipeline schema
~~~~~~~~~~~~~~~

.. image:: ../schema/caps.diffusion_estimation.py_tensor_estimation.FourthOrderTensorEstimation.png
    :height: 400px
    :align: center

