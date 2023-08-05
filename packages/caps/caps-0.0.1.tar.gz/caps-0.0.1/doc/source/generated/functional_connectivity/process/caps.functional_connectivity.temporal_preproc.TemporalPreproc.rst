.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

caps.functional_connectivity.temporal_preproc.TemporalPreproc
=============================================================


.. _caps.functional_connectivity.temporal_preproc.TemporalPreproc:


.. index:: TemporalPreproc

TemporalPreproc
---------------

.. currentmodule:: caps.functional_connectivity.temporal_preproc

.. autoclass:: TemporalPreproc
	:no-members:

Inputs
~~~~~~


[Mandatory]


[Optional]

+---------------------------------------------------------------------------+
| | **confounds_deriv**: a legal value (optional)                           |
| |     number of derivatives for each dimension [0]                        |
+---------------------------------------------------------------------------+
| | **confounds_dimensions**: a legal value (optional)                      |
| |      number of confound dimensions [defaults to using all dimensions    |
| |     available for each confound variable]                               |
+---------------------------------------------------------------------------+
| | **confounds_names**: a legal value (optional)                           |
| |     confounds names can be: 'Grey Matter', 'White Matter', 'CSF',any    |
| |     ROI name, any covariate name, or 'Effect of \*' where \*            |
| |     represents any condition name. Default to 'White Matter','CSF' and  |
| |     all covariates names                                                |
+---------------------------------------------------------------------------+
| | **despiking**: an integer (optional)                                    |
| |     1/0: temporal despiking with a hyperbolic tangent squashing         |
| |     function [1]                                                        |
+---------------------------------------------------------------------------+
| | **detrending**: an integer (optional)                                   |
| |     1/0: BOLD times-series detrending [1]                               |
+---------------------------------------------------------------------------+
| | **done**: an integer (optional)                                         |
| |     1/0, [0]. 0: only edits project fields (do not run                  |
| |     Preproc->'Done'); 1: run Preproc->'Done'                            |
+---------------------------------------------------------------------------+
| | **filter**: a legal value (optional)                                    |
| |     frequency filter (band-pass values, in Hz) [0.008,0.09]             |
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
