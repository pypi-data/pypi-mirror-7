.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

caps.functional_connectivity.setup.Setup
========================================


.. _caps.functional_connectivity.setup.Setup:


.. index:: Setup

Setup
-----

.. currentmodule:: caps.functional_connectivity.setup

.. autoclass:: Setup
	:no-members:

Inputs
~~~~~~


[Mandatory]

+-------------------------------------------------------------------------+
| | **anatomical_paths**: a legal value (mandatory)                       |
| |     paths to all subjects anatomical directories                      |
+-------------------------------------------------------------------------+
| | **anatomicals**: a legal value (mandatory)                            |
| |     the anatomical files                                              |
+-------------------------------------------------------------------------+
| | **anatomicals_from_spreproc**: a legal value (mandatory)              |
| |     the spatially preprocessed anatomical files, output from conn     |
| |     spatial preproc pipiline                                          |
+-------------------------------------------------------------------------+
| | **conditions_durations**: a legal value (mandatory)                   |
| |     Conditon durations                                                |
+-------------------------------------------------------------------------+
| | **conditions_names**: a legal value (mandatory)                       |
| |     Conditon names                                                    |
+-------------------------------------------------------------------------+
| | **conditions_onsets**: a legal value (mandatory)                      |
| |     Conditon onsets                                                   |
+-------------------------------------------------------------------------+
| | **functional_paths**: a legal value (mandatory)                       |
| |     paths to all subjects functional directories                      |
+-------------------------------------------------------------------------+
| | **functionals**: a legal value (mandatory)                            |
| |     the functional files                                              |
+-------------------------------------------------------------------------+
| | **functionals_from_spreproc**: a legal value (mandatory)              |
| |     the spatially preprocessed functional files, output from conn     |
| |     spatial preprocessing pipiline                                    |
+-------------------------------------------------------------------------+
| | **nconditions**: an integer (mandatory)                               |
| |     number of conditons                                               |
+-------------------------------------------------------------------------+
| | **nsubjects**: an integer (mandatory)                                 |
| |     Number of subjects                                                |
+-------------------------------------------------------------------------+
| | **rois_regresscovariates**: a legal value (mandatory)                 |
| |     Regress out covariates, default to 1 for more than one dimension  |
| |     extracted                                                         |
+-------------------------------------------------------------------------+
| | **sp_anatomical_prefix**: a string (mandatory)                        |
| |     the prefix of the spatially preprocessed anatomical images        |
+-------------------------------------------------------------------------+
| | **sp_functional_prefixes**: a legal value (mandatory)                 |
| |     the prefixes of the spatially preprocessed functional images      |
| |     associated to the sessions to include                             |
+-------------------------------------------------------------------------+

[Optional]

+---------------------------------------------------------------------------+
| | **CSF_masks_prefix**: a string (optional)                               |
| |     the prefix of spatially preprocessed CSF masks                      |
+---------------------------------------------------------------------------+
| | **Grey_masks_prefix**: a string (optional)                              |
| |     the prefix of spatially preprocessed Grey masks                     |
+---------------------------------------------------------------------------+
| | **White_masks_prefix**: a string (optional)                             |
| |     the prefix of spatially preprocessed White masks                    |
+---------------------------------------------------------------------------+
| | **analysis**: any value (optional)                                      |
| |     Vector of index to analysis types (1: ROI-to-ROI; 2: Seed-to-       |
| |     voxel; 3: Voxel-to-voxel) [1,2]                                     |
+---------------------------------------------------------------------------+
| | **covariates_files**: a legal value (optional)                          |
| |     covariates files                                                    |
+---------------------------------------------------------------------------+
| | **covariates_names**: a legal value (optional)                          |
| |     covariates names                                                    |
+---------------------------------------------------------------------------+
| | **covariates_prefixes**: a legal value (optional)                       |
| |     the prefixes of covariates files for all sessions, of length        |
| |     number of covariates                                                |
+---------------------------------------------------------------------------+
| | **done**: an integer (optional)                                         |
| |     1/0, [0]. 0: only edits project fields (do not run Setup->'Done');  |
| |     1: run Setup->'Done'                                                |
+---------------------------------------------------------------------------+
| | **isnew**: an integer (optional)                                        |
| |     1/0 is this a new conn project [0]                                  |
+---------------------------------------------------------------------------+
| | **masks_CSF_dimensions**: an integer (optional)                         |
| |     Number of PCA components extracted from the csf matter [16]         |
+---------------------------------------------------------------------------+
| | **masks_CSF_files**: a legal value (optional)                           |
| |     CSF mask volume file [defaults to CSF mask extracted from           |
| |     structural volume]                                                  |
+---------------------------------------------------------------------------+
| | **masks_Grey_dimensions**: an integer (optional)                        |
| |     Number of PCA components extracted from the grey matter [1]         |
+---------------------------------------------------------------------------+
| | **masks_Grey_files**: a legal value (optional)                          |
| |     grey matter mask volume file [defaults to Grey mask extracted from  |
| |     structural volume]                                                  |
+---------------------------------------------------------------------------+
| | **masks_White_dimensions**: an integer (optional)                       |
| |     Number of PCA components extracted from the white matter [16]       |
+---------------------------------------------------------------------------+
| | **masks_White_files**: a legal value (optional)                         |
| |     white matter mask volume file [defaults to White mask extracted     |
| |     from structural volume]                                             |
+---------------------------------------------------------------------------+
| | **normalized**: an integer (optional)                                   |
| |     1/0 are the spatially preprocessed images normalizedor not          |
+---------------------------------------------------------------------------+
| | **overwrite**: a legal value (optional)                                 |
| |     overwrite existing results if they exist ['Yes']                    |
+---------------------------------------------------------------------------+
| | **rois_dimensions**: a legal value (optional)                           |
| |     number of dimensions characterizing each ROI activation. (1         |
| |     represents only the mean BOLD activity within the ROI; 2 and above  |
| |     includes additional PCA [1]                                         |
+---------------------------------------------------------------------------+
| | **rois_files**: a legal value (optional)                                |
| |     List of ROIs files                                                  |
+---------------------------------------------------------------------------+
| | **rois_mask**: a legal value (optional)                                 |
| |     Mask with Grey Matter [0]                                           |
+---------------------------------------------------------------------------+
| | **rois_multiplelabels**: a legal value (optional)                       |
| |     Multiple ROIs, default to 1 for .nii or .img ROI files if           |
| |     associated .txt or .csv or .xls files exist                         |
+---------------------------------------------------------------------------+
| | **rois_names**: a legal value (optional)                                |
| |     ROIs names, default to ROIs files                                   |
+---------------------------------------------------------------------------+
| | **t_r**: a float (optional)                                             |
| |     Repetition time (seconds) [2]                                       |
+---------------------------------------------------------------------------+

Outputs
~~~~~~~

+--------------------------------------------------+
| | **conn_batch**: a legal value                  |
| |     the generated conn batch                   |
+--------------------------------------------------+
| | **setup_dict**: a legal value                  |
| |     dictionary with all conn setup parameters  |
+--------------------------------------------------+
