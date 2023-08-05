.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

caps.functional_connectivity.manager.InputDataManager
=====================================================


.. _caps.functional_connectivity.manager.InputDataManager:


.. index:: InputDataManager

InputDataManager
----------------

.. currentmodule:: caps.functional_connectivity.manager

.. autoclass:: InputDataManager
	:no-members:

Inputs
~~~~~~


[Mandatory]

+--------------------------------------------------+
| | **anatomical_dir_name**: a string (mandatory)  |
| |     the anatomical directory name              |
+--------------------------------------------------+
| | **data_path**: a directory name (mandatory)    |
| |     the path to all subject datasets           |
+--------------------------------------------------+
| | **functional_dir_name**: a string (mandatory)  |
| |     the functional directory name              |
+--------------------------------------------------+

[Optional]

+-----------------------------------------------------------------------+
| | **subjects**: a legal value (optional)                              |
| |     selection of specific subject directories. If unspecified, all  |
| |     present subdirectories in the data path are included            |
+-----------------------------------------------------------------------+

Outputs
~~~~~~~

+-----------------------------------------------------+
| | **anatomical_paths**: a legal value               |
| |     paths to all subjects anatomical directories  |
+-----------------------------------------------------+
| | **functional_paths**: a legal value               |
| |     paths to all subjects functional directories  |
+-----------------------------------------------------+
