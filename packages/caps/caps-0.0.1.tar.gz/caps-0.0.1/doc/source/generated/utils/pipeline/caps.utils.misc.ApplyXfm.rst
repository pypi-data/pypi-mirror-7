.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

caps.utils.misc.ApplyXfm
========================


.. _caps.utils.misc.ApplyXfm:


.. index:: ApplyXfm

ApplyXfm
--------

.. currentmodule:: caps.utils.misc

.. autoclass:: ApplyXfm
	:no-members:

Inputs
~~~~~~


[Mandatory]

+-------------------------------------------------+
| | **moving_image**: a file name (mandatory)     |
| |     input file                                |
+-------------------------------------------------+
| | **reference_image**: a file name (mandatory)  |
| |     reference file                            |
+-------------------------------------------------+

[Optional]

+-----------------------------------------------+
| | **in_matrix_file**: a file name (optional)  |
| |     input 4x4 affine matrix                 |
+-----------------------------------------------+

Outputs
~~~~~~~

+----------------------------------------------------+
| | **register_image**: a file name                  |
| |     path/name of registered file (if generated)  |
+----------------------------------------------------+

Pipeline schema
~~~~~~~~~~~~~~~

.. image:: ../schema/caps.utils.misc.ApplyXfm.png
    :height: 400px
    :align: center

