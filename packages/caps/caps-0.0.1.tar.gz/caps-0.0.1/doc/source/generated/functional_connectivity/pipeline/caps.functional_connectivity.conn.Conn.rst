.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

caps.functional_connectivity.conn.Conn
======================================


.. _caps.functional_connectivity.conn.Conn:


.. index:: Conn

Conn
----

.. currentmodule:: caps.functional_connectivity.conn

.. autoclass:: Conn
	:no-members:

Inputs
~~~~~~


[Mandatory]

+-------------------------------------------------------------------------+
| | **anatomical_dir_name**: a string (mandatory)                         |
| |     the anatomical directory name                                     |
+-------------------------------------------------------------------------+
| | **anatomicals**: a legal value (mandatory)                            |
| |     the anatomical files                                              |
+-------------------------------------------------------------------------+
| | **data_path**: a directory name (mandatory)                           |
| |     the path to all subject datasets                                  |
+-------------------------------------------------------------------------+
| | **functional_dir_name**: a string (mandatory)                         |
| |     the functional directory name                                     |
+-------------------------------------------------------------------------+
| | **functionals**: a legal value (mandatory)                            |
| |     the functional files                                              |
+-------------------------------------------------------------------------+
| | **nconditions**: an integer (mandatory)                               |
| |     number of conditons                                               |
+-------------------------------------------------------------------------+
| | **nsubjects**: an integer (mandatory)                                 |
| |     Number of subjects                                                |
+-------------------------------------------------------------------------+
| | **raw_anatomical_images**: a legal value (mandatory)                  |
| |     the anatomical files to spatially preprocess                      |
+-------------------------------------------------------------------------+
| | **raw_anatomical_prefix**: a string (mandatory)                       |
| |     the prefix of the raw anatomical images                           |
+-------------------------------------------------------------------------+
| | **raw_functional_images**: a legal value (mandatory)                  |
| |     the functional files to spatially preprocess                      |
+-------------------------------------------------------------------------+
| | **raw_functional_prefixes**: a legal value (mandatory)                |
| |     the prefixes of the raw functional imagesassociated to the        |
| |     sessions to include                                               |
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
| | **steps**: a legal value (mandatory)                                  |
| |     spatial preprocessing steps. Default to all steps:                |
| |     ['segmentation','slicetiming',                                    |
| |     'realignment','coregistration','normalization', 'smoothing']      |
+-------------------------------------------------------------------------+
| | **t_r**: a float (mandatory)                                          |
| |     Repetition time (seconds) [2]                                     |
+-------------------------------------------------------------------------+

[Optional]


Outputs
~~~~~~~

+--------------------------------------------------+
| | **CSF_masks**: any value                       |
+--------------------------------------------------+
| | **White_masks**: any value                     |
+--------------------------------------------------+
| | **conn_batch_analysis**: a legal value         |
| |     the generated conn batch                   |
+--------------------------------------------------+
| | **conn_batch_results**: a legal value          |
| |     the generated conn batch                   |
+--------------------------------------------------+
| | **conn_batch_setup**: a legal value            |
| |     the generated conn batch                   |
+--------------------------------------------------+
| | **conn_batch_tpreproc**: a legal value         |
| |     the generated conn batch                   |
+--------------------------------------------------+
| | **setup_dict**: a legal value                  |
| |     dictionary with all conn setup parameters  |
+--------------------------------------------------+

Pipeline schema
~~~~~~~~~~~~~~~

.. image:: ../schema/caps.functional_connectivity.conn.Conn.png
    :height: 400px
    :align: center

