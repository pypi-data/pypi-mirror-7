.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

caps.functional_connectivity.analysis.Analysis
==============================================


.. _caps.functional_connectivity.analysis.Analysis:


.. index:: Analysis

Analysis
--------

.. currentmodule:: caps.functional_connectivity.analysis

.. autoclass:: Analysis
	:no-members:

Inputs
~~~~~~


[Mandatory]


[Optional]

+---------------------------------------------------------------------------+
| | **analysis_number**: a legal value (optional)                           |
| |     sequential indexes identifying each set of independent analyses     |
| |     (set this variable to 0 to identify voxel-to-voxel analyses) [1]    |
+---------------------------------------------------------------------------+
| | **done**: an integer (optional)                                         |
| |     1/0, [0]. 0: only edits Analysis fields (do not run                 |
| |     Analysis->'Done'); 1: run Analysis->'Done'                          |
+---------------------------------------------------------------------------+
| | **measure**: an integer (optional)                                      |
| |     ROI-to-ROI and seed-to-voxel connectivity measure used, 1 =         |
| |     'correlation (bivariate)', 2 = 'correlation (semipartial)', 3 =     |
| |     'regression (bivariate)', 4 = 'regression (multivariate)'; [1]      |
+---------------------------------------------------------------------------+
| | **measures_dimensions**: a legal value (optional)                       |
| |     voxel-to-voxel number of SVD dimensions to retain (dimensionality   |
| |     reduction) [16]                                                     |
+---------------------------------------------------------------------------+
| | **measures_kernelshape**: a legal value (optional)                      |
| |     voxel-to-voxel kernel shape (0: gaussian; 1: gradient; 2:           |
| |     laplacian) [1]                                                      |
+---------------------------------------------------------------------------+
| | **measures_kernelsupport**: a legal value (optional)                    |
| |     voxel-to-voxel kernel supportlocal support (FWHM) of smoothing      |
| |     kernel [12]                                                         |
+---------------------------------------------------------------------------+
| | **measures_names**: a legal value (optional)                            |
| |     voxel-to-voxel measure names. Possible measure names are            |
| |     'connectome-MVPA', 'IntegratedLocalCorrelation',                    |
| |     'RadialCorrelationContrast' 'IntrinsicConnectivityContrast',        |
| |     'RadalSimilarityContrast'(if this variable does not exist the       |
| |     toolbox will perform the analyses for all of the default voxel-to-  |
| |     voxel measures)                                                     |
+---------------------------------------------------------------------------+
| | **measures_type**: a legal value (optional)                             |
| |     voxel-to-voxel measure type0:local measures; 1: global measures     |
| |     [1]                                                                 |
+---------------------------------------------------------------------------+
| | **overwrite**: a legal value (optional)                                 |
| |     overwrite existing results if they exist ['Yes']                    |
+---------------------------------------------------------------------------+
| | **sources_derivatives**: a legal value (optional)                       |
| |     number of derivatives for each dimension [0]                        |
+---------------------------------------------------------------------------+
| | **sources_dimensions**: a legal value (optional)                        |
| |     ROI-to-ROI and seed-to-voxel number of source dimensions [1]        |
+---------------------------------------------------------------------------+
| | **sources_names**: a legal value (optional)                             |
| |     ROI-to-ROI and seed-to-voxel sources names (seeds) for              |
| |     connectivity analyses - these correspond to a subset of ROI file    |
| |     names in the ROI folder (if this variable does not exist the        |
| |     toolbox will perform the analyses for all of the ROI files          |
| |     imported in the Setup step which are not defined as confounds in    |
| |     the Preprocessing step)                                             |
+---------------------------------------------------------------------------+
| | **type**: an integer (optional)                                         |
| |     ROI-to-ROI and seed-to-voxel analysis type, 1 = 'ROI-to-ROI', 2 =   |
| |     'Seed-to-Voxel', 3 = 'all'; [3]                                     |
+---------------------------------------------------------------------------+
| | **weight**: an integer (optional)                                       |
| |     ROI-to-ROI and seed-to-voxel within-condition weight, 1 = 'none',   |
| |     2 = 'hrf', 3 = 'hanning'; [2]                                       |
+---------------------------------------------------------------------------+

Outputs
~~~~~~~

+----------------------------------+
| | **conn_batch**: a legal value  |
| |     the generated conn batch   |
+----------------------------------+
