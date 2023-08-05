.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

caps.functional_connectivity.results.Results
============================================


.. _caps.functional_connectivity.results.Results:


.. index:: Results

Results
-------

.. currentmodule:: caps.functional_connectivity.results

.. autoclass:: Results
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
| | **between_conditions_contrast**: a legal value (optional)               |
| |     between_conditions contrast vector (same size as                    |
| |     between_conditions_effect_names)                                    |
+---------------------------------------------------------------------------+
| | **between_conditions_effect_names**: a legal value (optional)           |
| |     condition names (as in Setup.conditions.names) [defaults to         |
| |     multiple analyses, one per condition].                              |
+---------------------------------------------------------------------------+
| | **between_sources_contrast**: a legal value (optional)                  |
| |     between_sources contrast vector (same size as                       |
| |     between_sources_effect_names)                                       |
+---------------------------------------------------------------------------+
| | **between_sources_effect_names**: a legal value (optional)              |
| |     sources names. (as in Analysis.regressors, typically appended with  |
| |     _1_1; generally they are appended with _N_M -where N is an index    |
| |     ranging from 1 to 1+derivative order, and M is an index ranging     |
| |     from 1 to the number of dimensions specified for each ROI; for      |
| |     example ROINAME_2_3 corresponds to the first derivative of the      |
| |     third PCA component extracted from the roi ROINAME) [defaults to    |
| |     multiple analyses, one per source].                                 |
+---------------------------------------------------------------------------+
| | **between_subjects_contrast**: a legal value (optional)                 |
| |     between_subjects contrast vector (same size as                      |
| |     between_subjects_effect_names)                                      |
+---------------------------------------------------------------------------+
| | **between_subjects_effect_names**: a legal value (optional)             |
| |     second-level effect names                                           |
+---------------------------------------------------------------------------+
| | **done**: an integer (optional)                                         |
| |     1/0, [0]. 0: only edits Results fields (do not run                  |
| |     Results->'Done'); 1: run Results->'Done'                            |
+---------------------------------------------------------------------------+
| | **foldername**: a directory name (optional)                             |
| |     folder to store the results                                         |
+---------------------------------------------------------------------------+
| | **overwrite**: a legal value (optional)                                 |
| |     overwrite existing results if they exist ['Yes']                    |
+---------------------------------------------------------------------------+

Outputs
~~~~~~~

+----------------------------------+
| | **conn_batch**: a legal value  |
| |     the generated conn batch   |
+----------------------------------+
