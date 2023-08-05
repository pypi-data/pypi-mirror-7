.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

caps.diffusion_estimation.fsl_tensor_estimation.FSLTensorEstimation
===================================================================


.. _caps.diffusion_estimation.fsl_tensor_estimation.FSLTensorEstimation:


.. index:: FSLTensorEstimation

FSLTensorEstimation
-------------------

.. currentmodule:: caps.diffusion_estimation.fsl_tensor_estimation

.. autoclass:: FSLTensorEstimation
	:no-members:

Inputs
~~~~~~


[Mandatory]

+-------------------------------------------+
| | **bvals**: a file name (mandatory)      |
| |     b values file                       |
+-------------------------------------------+
| | **bvecs**: a file name (mandatory)      |
| |     b vectors file                      |
+-------------------------------------------+
| | **dw_image**: a file name (mandatory)   |
| |     diffusion weighted image data file  |
+-------------------------------------------+
| | **mask**: a file name (mandatory)       |
| |     bet binary mask file                |
+-------------------------------------------+

[Optional]


Outputs
~~~~~~~

+---------------------------------------------------------+
| | **fractional_anisotropy**: a file name                |
| |     path/name of file with the fractional anisotropy  |
+---------------------------------------------------------+
| | **mean_diffusivity**: a file name                     |
| |     path/name of file with the mean diffusivity       |
+---------------------------------------------------------+
| | **tensor**: a file name                               |
| |     path/name of file with the 4D tensor volume       |
+---------------------------------------------------------+

Pipeline schema
~~~~~~~~~~~~~~~

.. image:: ../schema/caps.diffusion_estimation.fsl_tensor_estimation.FSLTensorEstimation.png
    :height: 400px
    :align: center

