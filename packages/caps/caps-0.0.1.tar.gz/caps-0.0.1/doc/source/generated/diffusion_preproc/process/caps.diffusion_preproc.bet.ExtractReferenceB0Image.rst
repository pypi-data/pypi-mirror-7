.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

caps.diffusion_preproc.bet.ExtractReferenceB0Image
==================================================


.. _caps.diffusion_preproc.bet.ExtractReferenceB0Image:


.. index:: ExtractReferenceB0Image

ExtractReferenceB0Image
-----------------------

.. currentmodule:: caps.diffusion_preproc.bet

.. autoclass:: ExtractReferenceB0Image
	:no-members:

Inputs
~~~~~~


[Mandatory]

+---------------------------------------------+
| | **bvals**: a file name (mandatory)        |
| |     the the diffusion b-values            |
+---------------------------------------------+
| | **dw_image**: a file name (mandatory)     |
| |     an existing diffusion weighted image  |
+---------------------------------------------+

[Optional]

+------------------------------------------------------------+
| | **specified_index_of_ref_image**: an integer (optional)  |
| |     index of the reference b=0 volume                    |
+------------------------------------------------------------+

Outputs
~~~~~~~

+------------------------------------------+
| | **index_of_ref_image**: an integer     |
| |     index of the reference b=0 volume  |
+------------------------------------------+
