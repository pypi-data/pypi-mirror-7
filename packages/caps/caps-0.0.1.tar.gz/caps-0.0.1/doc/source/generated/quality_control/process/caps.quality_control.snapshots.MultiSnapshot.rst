.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

caps.quality_control.snapshots.MultiSnapshot
============================================


.. _caps.quality_control.snapshots.MultiSnapshot:


.. index:: MultiSnapshot

MultiSnapshot
-------------

.. currentmodule:: caps.quality_control.snapshots

.. autoclass:: MultiSnapshot
	:no-members:

Inputs
~~~~~~


[Mandatory]

+-----------------------------------------+
| | **in_file**: a file name (mandatory)  |
| |     volume to treat                   |
+-----------------------------------------+
| | **lower_bound**: a float (mandatory)  |
| |     the lower bound slice fraction    |
+-----------------------------------------+
| | **nb_steps**: an integer (mandatory)  |
| |     desired number of snapshots       |
+-----------------------------------------+
| | **upper_bound**: a float (mandatory)  |
| |     the upper bound slice fraction    |
+-----------------------------------------+

[Optional]

+------------------------------------------------------------------+
| | **output_dir**: a directory name (optional)                    |
| |     output directory                                           |
+------------------------------------------------------------------+
| | **target**: a file name (optional)                             |
| |     the location of the target image to display edge overlay.  |
+------------------------------------------------------------------+

Outputs
~~~~~~~

+----------------------------------------+
| | **image_out**: a string              |
| |     path of the png resulting image  |
+----------------------------------------+
