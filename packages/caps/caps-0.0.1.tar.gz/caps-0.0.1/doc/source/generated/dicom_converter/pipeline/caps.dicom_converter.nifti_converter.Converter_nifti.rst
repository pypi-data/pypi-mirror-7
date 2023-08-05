.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

caps.dicom_converter.nifti_converter.Converter_nifti
====================================================


.. _caps.dicom_converter.nifti_converter.Converter_nifti:


.. index:: Converter_nifti

Converter_nifti
---------------

.. currentmodule:: caps.dicom_converter.nifti_converter

.. autoclass:: Converter_nifti
	:no-members:

Inputs
~~~~~~


[Mandatory]

+---------------------------------------------------------------------------+
| | **terminal_output**: a legal value (mandatory)                          |
| |     Control terminal output: `stream` - displays to terminal            |
| |     immediately, `allatonce` - waits till command is finished to        |
| |     display output, `file` - writes output to file, `none` - output is  |
| |     ignored                                                             |
+---------------------------------------------------------------------------+

[Optional]


Outputs
~~~~~~~

+----------------------------------------------------+
| | **_bvals**: a legal value or a file name         |
+----------------------------------------------------+
| | **_bvecs**: a legal value or a file name         |
+----------------------------------------------------+
| | **filled_nifti_gz_file**: a file name            |
+----------------------------------------------------+
| | **nifti_gz_file**: a legal value or a file name  |
+----------------------------------------------------+

Pipeline schema
~~~~~~~~~~~~~~~

.. image:: ../schema/caps.dicom_converter.nifti_converter.Converter_nifti.png
    :height: 400px
    :align: center

