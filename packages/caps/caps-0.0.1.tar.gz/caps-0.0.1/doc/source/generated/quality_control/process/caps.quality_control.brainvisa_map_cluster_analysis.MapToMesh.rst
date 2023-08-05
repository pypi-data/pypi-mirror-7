.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

caps.quality_control.brainvisa_map_cluster_analysis.MapToMesh
=============================================================


.. _caps.quality_control.brainvisa_map_cluster_analysis.MapToMesh:


.. index:: MapToMesh

MapToMesh
---------

.. currentmodule:: caps.quality_control.brainvisa_map_cluster_analysis

.. autoclass:: MapToMesh
	:no-members:

Inputs
~~~~~~


[Mandatory]

+----------------------------------------------------------------+
| | **thresh_neg_bound**: any value (mandatory)                  |
| |     Negative bound threshold (lower, upper)                  |
+----------------------------------------------------------------+
| | **thresh_pos_bound**: any value (mandatory)                  |
| |     Positivee bound threshold (lower, upper)                 |
+----------------------------------------------------------------+
| | **thresh_size**: an integer (mandatory)                      |
| |     Threshold, in voxels nb, between small and big clusters  |
+----------------------------------------------------------------+
| | **wmap_file**: a file name (mandatory)                       |
| |     Input map volume                                         |
+----------------------------------------------------------------+

[Optional]


Outputs
~~~~~~~

+------------------------------------------+
| | **cluster_file**: a file name          |
| |     Cluster file                       |
+------------------------------------------+
| | **cluster_mask_file**: a file name     |
| |     Cluster mask file                  |
+------------------------------------------+
| | **connected_components**: a file name  |
| |     Connected components               |
+------------------------------------------+
| | **mesh_file**: a file name             |
| |     Mesh file                          |
+------------------------------------------+
