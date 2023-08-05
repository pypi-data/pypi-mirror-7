.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

caps.preclinic_functional.spm_realignment.Realignment
=====================================================


.. _caps.preclinic_functional.spm_realignment.Realignment:


.. index:: Realignment

Realignment
-----------

.. currentmodule:: caps.preclinic_functional.spm_realignment

.. autoclass:: Realignment
	:no-members:

Inputs
~~~~~~


[Mandatory]

+---------------------------------------------------------------+
| | **register_to_mean**: a boolean (mandatory)                 |
| |     Indicate whether realignment is done to the mean image  |
+---------------------------------------------------------------+

[Optional]


Outputs
~~~~~~~

+-------------------------------------------------------------+
| | **realigned_time_series_header_modified**: a file name    |
+-------------------------------------------------------------+
| | **realigned_time_series_image**: a file name              |
+-------------------------------------------------------------+
| | **realignment_parameters**: a legal value or a file name  |
| |     Estimated translation and rotation parameters         |
+-------------------------------------------------------------+
| | **reference_mean_image**: a file name                     |
+-------------------------------------------------------------+

Pipeline schema
~~~~~~~~~~~~~~~

.. image:: ../schema/caps.preclinic_functional.spm_realignment.Realignment.png
    :height: 400px
    :align: center

