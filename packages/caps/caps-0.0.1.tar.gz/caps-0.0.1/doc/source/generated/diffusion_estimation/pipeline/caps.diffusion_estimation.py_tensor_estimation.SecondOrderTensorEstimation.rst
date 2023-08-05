.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

caps.diffusion_estimation.py_tensor_estimation.SecondOrderTensorEstimation
==========================================================================


.. _caps.diffusion_estimation.py_tensor_estimation.SecondOrderTensorEstimation:


.. index:: SecondOrderTensorEstimation

SecondOrderTensorEstimation
---------------------------

.. currentmodule:: caps.diffusion_estimation.py_tensor_estimation

.. autoclass:: SecondOrderTensorEstimation
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


Outputs
~~~~~~~

+----------------------------------------------------------------------+
| | **eigen_values_file**: a file name                                 |
| |     the name of the output eigen values file                       |
+----------------------------------------------------------------------+
| | **eigen_vectors_file**: a file name                                |
| |     the name of the output eigen vectors file                      |
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
| | **tensor_file**: any value                                         |
+----------------------------------------------------------------------+

Pipeline schema
~~~~~~~~~~~~~~~

.. image:: ../schema/caps.diffusion_estimation.py_tensor_estimation.SecondOrderTensorEstimation.png
    :height: 400px
    :align: center

