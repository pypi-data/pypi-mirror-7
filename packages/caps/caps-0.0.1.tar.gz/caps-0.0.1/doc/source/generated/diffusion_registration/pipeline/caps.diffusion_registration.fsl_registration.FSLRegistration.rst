.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

caps.diffusion_registration.fsl_registration.FSLRegistration
============================================================


.. _caps.diffusion_registration.fsl_registration.FSLRegistration:


.. index:: FSLRegistration

FSLRegistration
---------------

.. currentmodule:: caps.diffusion_registration.fsl_registration

.. autoclass:: FSLRegistration
	:no-members:

Inputs
~~~~~~


[Mandatory]

+---------------------------------------------+
| | **fa_file**: a file name (mandatory)      |
| |     input file                            |
+---------------------------------------------+
| | **target_file**: a file name (mandatory)  |
| |     reference file                        |
+---------------------------------------------+
| | **tensor_file**: a file name (mandatory)  |
| |     image to be warped                    |
+---------------------------------------------+

[Optional]

+--------------------------------------------------------------+
| | **config_file**: a legal value or a file name (optional)   |
| |     Name of config file specifying command line arguments  |
+--------------------------------------------------------------+
| | **mask_file**: a file name (optional)                      |
| |     File for input weighting volume                        |
+--------------------------------------------------------------+

Outputs
~~~~~~~

+--------------------------------------------+
| | **fa_warped_file**: a file name          |
| |     warped image                         |
+--------------------------------------------+
| | **field_file**: a file name              |
| |     file with warp field                 |
+--------------------------------------------+
| | **fieldcoeff_file**: a file name         |
| |     file with field coefficients         |
+--------------------------------------------+
| | **reoriented_tensor_file**: a file name  |
| |     the reoriented tensor field          |
+--------------------------------------------+
| | **tensor_warped_file**: a file name      |
| |     Warped output file                   |
+--------------------------------------------+

Pipeline schema
~~~~~~~~~~~~~~~

.. image:: ../schema/caps.diffusion_registration.fsl_registration.FSLRegistration.png
    :height: 400px
    :align: center

