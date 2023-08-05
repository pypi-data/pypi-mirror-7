.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

caps.quality_control.snapshots.Snap
===================================


.. _caps.quality_control.snapshots.Snap:


.. index:: Snap

Snap
----

.. currentmodule:: caps.quality_control.snapshots

.. autoclass:: Snap
	:no-members:

Inputs
~~~~~~


[Mandatory]

+---------------------------------------------+
| | **input_image**: a file name (mandatory)  |
| |     input volume                          |
+---------------------------------------------+
| | **lower_bound**: a float (mandatory)      |
| |     the lower bound slice fraction        |
+---------------------------------------------+
| | **nb_steps**: an integer (mandatory)      |
| |     desired number of snapshots           |
+---------------------------------------------+
| | **upper_bound**: a float (mandatory)      |
| |     the upper bound slice fraction        |
+---------------------------------------------+

[Optional]

+----------------------------------------------------------------+
| | **edges_image**: a file name (optional)                      |
| |     volume to display edge overlay for (useful for checking  |
| |     registration                                             |
+----------------------------------------------------------------+

Outputs
~~~~~~~

+-----------------------------+
| | **image_out**: any value  |
+-----------------------------+

Pipeline schema
~~~~~~~~~~~~~~~

.. image:: ../schema/caps.quality_control.snapshots.Snap.png
    :height: 400px
    :align: center

