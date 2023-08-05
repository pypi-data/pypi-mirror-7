.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

caps.diffusion_preproc.susceptibility_correction.SusceptibilityCorrection
=========================================================================


.. _caps.diffusion_preproc.susceptibility_correction.SusceptibilityCorrection:


.. index:: SusceptibilityCorrection

SusceptibilityCorrection
------------------------

.. currentmodule:: caps.diffusion_preproc.susceptibility_correction

.. autoclass:: SusceptibilityCorrection
	:no-members:

Inputs
~~~~~~


[Mandatory]

+----------------------------------------------------+
| | **complex_phase_file**: a file name (mandatory)  |
| |     complex phase input volume                   |
+----------------------------------------------------+
| | **magnitude_file**: a file name (mandatory)      |
| |     file containing magnitude image              |
+----------------------------------------------------+
| | **phase_file**: a file name (mandatory)          |
| |     raw phase file                               |
+----------------------------------------------------+

[Optional]

+------------------------------------------+
| | **dw_file**: a file name (optional)    |
| |     filename of input volume           |
+------------------------------------------+
| | **mask_file**: a file name (optional)  |
| |     filename of mask input volume      |
+------------------------------------------+

Outputs
~~~~~~~

+---------------------------------------------------+
| | **susceptibility_corrected_file**: a file name  |
| |     unwarped file                               |
+---------------------------------------------------+
| | **unwrapped_phase_file**: a file name           |
| |     unwrapped phase file                        |
+---------------------------------------------------+

Pipeline schema
~~~~~~~~~~~~~~~

.. image:: ../schema/caps.diffusion_preproc.susceptibility_correction.SusceptibilityCorrection.png
    :height: 400px
    :align: center

