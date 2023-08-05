.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

.. _example_caps.functional_connectivity.conn.pilot :

====
Conn
====

.. hidden-code-block:: python
    :starthidden: True

    # The full use case code: caps.functional_connectivity.conn.pilot
    from caps.toy_datasets import get_sample_data
    import numpy
        from capsul.study_config import StudyConfig
    from capsul.utils.sorted_dictionary import SortedDictionary
    from caps.dicom_converter.base.tools import ensure_is_dir
    from caps.functional_connectivity.conn import Conn
    
        toy_dataset = get_sample_data("conn")
    print(toy_dataset.anatomicals, toy_dataset.functionals)
    conn_pipeline = Conn()

    conn_pipeline.data_path = "/volatile/new/salma/NYU_TRT_session1a/"
    conn_pipeline.functional_dir_name = "func"
    conn_pipeline.anatomical_dir_name = "anat"
    conn_pipeline.sp_functional_prefixes = ["swralfo*.nii"]
    conn_pipeline.sp_anatomical_prefix = "wmmprage_a*.nii"
    conn_pipeline.Grey_masks_prefix = "mwc1mprage_a*.nii"
    conn_pipeline.White_masks_prefix = "mwc2mprage_a*.nii"
    conn_pipeline.CSF_masks_prefix = "mwc3mprage_a*.nii"
    conn_pipeline.covariates_names = ["Realignment"]
    conn_pipeline.covariates_prefixes = [["rp_alfo*.txt"]]
    conn_pipeline.conditions_names = ["Session"]
    conn_pipeline.conditions_onsets = [[[numpy.nan if nsess != ncond else 0
    for nsess in range(1)] for nsub in xrange(3)] for ncond in range(1)]  # TODO: move it to manager?
    conn_pipeline.conditions_durations = [[[numpy.nan if nsess != ncond else 
    numpy.inf for nsess in range(1)] for nsub in xrange(1)]for ncond in range(1)] # TODO: move it to manager?
    conn_pipeline.raw_functional_prefixes = ["lfo*.nii"]
    conn_pipeline.raw_anatomical_prefix = "mprage_a*.nii"
    conn_pipeline.steps = ["segmentation", "realignment", "coregistration",
                      "normalization", "smoothing"]    setup = Setup()
    setup.batch_header = spreproc.batch
    setup.functionals = manager.spreproc_functional_images
    setup.anatomicals = manager.spreproc_anatomical_images
    setup.conditions_names = ["Session"]
    setup.conditions_onsets = [[[numpy.nan if nsess != ncond else 0
    for nsess in xrange(setup.nconditions)] for nsub in xrange(setup.nsubjects
    )] for ncond in xrange(setup.nconditions)] # TODO: move it to manager?
    setup.conditions_durations = [[[numpy.nan if nsess != ncond else numpy.inf
    for nsess in xrange(setup.nconditions)] for nsub in xrange(setup.nsubjects
    )]for ncond in xrange(setup.nconditions)] # TODO: move it to manager?
    setup.overwrite = "No"
    setup = Setup()
    setup.batch_header = spreproc.batch
    setup.functionals = manager.spreproc_functional_images
    setup.anatomicals = manager.spreproc_anatomical_images
    setup.conditions_names = ["Session"]
    setup.conditions_onsets = [[[numpy.nan if nsess != ncond else 0
    for nsess in xrange(setup.nconditions)] for nsub in xrange(setup.nsubjects
    )] for ncond in xrange(setup.nconditions)] # TODO: move it to manager?
    setup.conditions_durations = [[[numpy.nan if nsess != ncond else numpy.inf
    for nsess in xrange(setup.nconditions)] for nsub in xrange(setup.nsubjects
    )]for ncond in xrange(setup.nconditions)] # TODO: move it to manager?
    setup.overwrite = "No"
    """
    Will return the input parameters the user can set:

    .. code-block:: python

        INPUT SPECIFICATIONS

        do_motion_correction: ['Enum']
        do_susceptibility_correction: ['Enum']
        dw_image: ['File']
        bvals: ['File']
        specified_index_of_ref_image: ['Int']
        bvecs: ['File']
        terminal_output: ['Enum']
        generate_binary_mask: ['Bool']
        use_4d_input: ['Bool']
        generate_mesh: ['Bool']
        generate_skull: ['Bool']
        bet_threshold: ['Float']
        magnitude_file: ['File']
        phase_file: ['File']
        complex_phase_file: ['File']

    We can now tune the pipeline parameters.
    We first set the input dwi file and associated b-values and b-vectors:    fsl_preproc_pipeline.dw_image = toy_dataset.dwi
    fsl_preproc_pipeline.bvals = toy_dataset.bvals
    fsl_preproc_pipeline.bvecs = toy_dataset.bvecs
    fsl_preproc_pipeline.do_motion_correction = "YES"
    fsl_preproc_pipeline.do_susceptibility_correction = "YES"
    conn_working_dir = os.path.join(working_dir, "conn")
    # ensure_is_dir(preproc_working_dir)
    default_config = SortedDictionary(
        ("output_directory", conn_working_dir),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)
    # study.run(conn_pipeline)
    print "\nOUTPUTS\n"
    for trait_name, trait_value in conn_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)


.. topic:: Objective

    Wrapping of the functional connectivity toolbox CONN 
    (https://www.nitrc.org/projects/conn/). Parallelization 

Import
------

First we load the function that enables us to access the toy datasets

::

    from caps.toy_datasets import get_sample_data
    import numpy
    

From capsul we then load the class to configure the study we want to
perform

::

    from capsul.study_config import StudyConfig


Here two utility tools are loaded. The first one enables the creation
of ordered dictionary and the second ensure that a directory exist.
Note that the directory will be created if necessary.

::

    from capsul.utils.sorted_dictionary import SortedDictionary
    from caps.dicom_converter.base.tools import ensure_is_dir


Load the classes to configure the manager and the different steps of the 
functional connectivity pipeline

::

    from caps.functional_connectivity.conn import Conn
    
    

Load the toy dataset
--------------------

We want to perform BET on a diffusion sequence.
To do so, we use the *get_sample_data* function to load this
dataset.

.. seealso::

    For a complete description of the *get_sample_data* function, see the
    :ref:`Toy Datasets documentation <toy_datasets_guide>`

::

    toy_dataset = get_sample_data("conn")


The *toy_dataset* is an Enum structure with some specific
elements of interest *dwi*, *bvals*, *bvecs* that contain the nifti
diffusion image ,the b-values and the b-vectors respectively.

::

    print(toy_dataset.anatomicals, toy_dataset.functionals)


Will return:

.. code-block:: python

    /home/ag239446/git/nsap-src/nsap/data/DTI30s010.nii
    /home/ag239446/git/nsap-src/nsap/data/DTI30s010.bval
    /home/ag239446/git/nsap-src/nsap/data/DTI30s010.bvec

We can see that the image has been found in a local directory

Data Location
-------------
Now we give the data location and the prefixes of the images as input 
parameters for the manager:
* the path to the parent directory for all the subjects subdirectories, 
* the name of the functional and anatomical directories 
* the prefixes of the functional and anatomical images to include. 

The following tree is assumed:

.. code-block:: python

    manager.data_path
    |---manager.subjects[0]
    |    |---manager.functional_dir_name (folder or recursive folders)
    |    |    |---manager.raw_functional_prefixes[0]
    |    |    |
    |    |    |---manager.raw_functional_prefixes[-1]
    |    |    :
    |    |    :...other possible folders or files
    |    |
    |    |---manager.anatomical_dir_name (folder or recursive folders)
    |    |    |---manager.raw_anatomical_prefix
    |    |    :
    |    |    :...other possible files
    |    |
    |    :...other possible folders or files
    |
    |---manager.subjects[-1]
    |    |---manager.functional_dir_name
    |    |    |---manager.raw_functional_prefixes[0]
    |    |    :
    |    |    |---manager.raw_functional_prefixes[-1]
    |    |    :
    |    |---manager.anatomical_dir_name
    |    |    |---manager.raw_anatomical_prefix
    |    |    :
    |    :
    |
    :...other possible folders or files     

::

    conn_pipeline = Conn()

    conn_pipeline.data_path = "/volatile/new/salma/NYU_TRT_session1a/"
    conn_pipeline.functional_dir_name = "func"
    conn_pipeline.anatomical_dir_name = "anat"
    conn_pipeline.sp_functional_prefixes = ["swralfo*.nii"]
    conn_pipeline.sp_anatomical_prefix = "wmmprage_a*.nii"
    conn_pipeline.Grey_masks_prefix = "mwc1mprage_a*.nii"
    conn_pipeline.White_masks_prefix = "mwc2mprage_a*.nii"
    conn_pipeline.CSF_masks_prefix = "mwc3mprage_a*.nii"
    conn_pipeline.covariates_names = ["Realignment"]
    conn_pipeline.covariates_prefixes = [["rp_alfo*.txt"]]
    conn_pipeline.conditions_names = ["Session"]
    conn_pipeline.conditions_onsets = [[[numpy.nan if nsess != ncond else 0
    for nsess in range(1)] for nsub in xrange(3)] for ncond in range(1)]  # TODO: move it to manager?
    conn_pipeline.conditions_durations = [[[numpy.nan if nsess != ncond else 
    numpy.inf for nsess in range(1)] for nsub in xrange(1)]for ncond in range(1)] # TODO: move it to manager?


You can run a complete or a partial spatial preprocessing pipeline on the
data, or simply skip this step if your data has been already spatially
preprocessed.

::

    conn_pipeline.raw_functional_prefixes = ["lfo*.nii"]
    conn_pipeline.raw_anatomical_prefix = "mprage_a*.nii"
    conn_pipeline.steps = ["segmentation", "realignment", "coregistration",
                      "normalization", "smoothing"]

Set the parameters for the Setup step

::

    setup = Setup()
    setup.batch_header = spreproc.batch
    setup.functionals = manager.spreproc_functional_images
    setup.anatomicals = manager.spreproc_anatomical_images
    setup.conditions_names = ["Session"]
    setup.conditions_onsets = [[[numpy.nan if nsess != ncond else 0
    for nsess in xrange(setup.nconditions)] for nsub in xrange(setup.nsubjects
    )] for ncond in xrange(setup.nconditions)] # TODO: move it to manager?
    setup.conditions_durations = [[[numpy.nan if nsess != ncond else numpy.inf
    for nsess in xrange(setup.nconditions)] for nsub in xrange(setup.nsubjects
    )]for ncond in xrange(setup.nconditions)] # TODO: move it to manager?
    setup.overwrite = "No"


Set the parameters for the Analysis step

::

    setup = Setup()
    setup.batch_header = spreproc.batch
    setup.functionals = manager.spreproc_functional_images
    setup.anatomicals = manager.spreproc_anatomical_images
    setup.conditions_names = ["Session"]
    setup.conditions_onsets = [[[numpy.nan if nsess != ncond else 0
    for nsess in xrange(setup.nconditions)] for nsub in xrange(setup.nsubjects
    )] for ncond in xrange(setup.nconditions)] # TODO: move it to manager?
    setup.conditions_durations = [[[numpy.nan if nsess != ncond else numpy.inf
    for nsess in xrange(setup.nconditions)] for nsub in xrange(setup.nsubjects
    )]for ncond in xrange(setup.nconditions)] # TODO: move it to manager?
    setup.overwrite = "No"
    """
    Will return the input parameters the user can set:

    .. code-block:: python

        INPUT SPECIFICATIONS

        do_motion_correction: ['Enum']
        do_susceptibility_correction: ['Enum']
        dw_image: ['File']
        bvals: ['File']
        specified_index_of_ref_image: ['Int']
        bvecs: ['File']
        terminal_output: ['Enum']
        generate_binary_mask: ['Bool']
        use_4d_input: ['Bool']
        generate_mesh: ['Bool']
        generate_skull: ['Bool']
        bet_threshold: ['Float']
        magnitude_file: ['File']
        phase_file: ['File']
        complex_phase_file: ['File']

    We can now tune the pipeline parameters.
    We first set the input dwi file and associated b-values and b-vectors:

Will return the input parameters the user can set:

.. code-block:: python

    INPUT SPECIFICATIONS

    do_motion_correction: ['Enum']
    do_susceptibility_correction: ['Enum']
    dw_image: ['File']
    bvals: ['File']
    specified_index_of_ref_image: ['Int']
    bvecs: ['File']
    terminal_output: ['Enum']
    generate_binary_mask: ['Bool']
    use_4d_input: ['Bool']
    generate_mesh: ['Bool']
    generate_skull: ['Bool']
    bet_threshold: ['Float']
    magnitude_file: ['File']
    phase_file: ['File']
    complex_phase_file: ['File']

We can now tune the pipeline parameters.
We first set the input dwi file and associated b-values and b-vectors:

::

    fsl_preproc_pipeline.dw_image = toy_dataset.dwi
    fsl_preproc_pipeline.bvals = toy_dataset.bvals
    fsl_preproc_pipeline.bvecs = toy_dataset.bvecs


We activate the motion correction

::

    fsl_preproc_pipeline.do_motion_correction = "YES"


And desactivate the susceptibility correction

::

    fsl_preproc_pipeline.do_susceptibility_correction = "YES"


Study Configuration
-------------------

The pipeline is now set up and ready to be executed.
For a complete description of a study execution, see the
:ref:`Study Configuration description <study_configuration_guide>`

::

    conn_working_dir = os.path.join(working_dir, "conn")
    # ensure_is_dir(preproc_working_dir)
    default_config = SortedDictionary(
        ("output_directory", conn_working_dir),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)
    # study.run(conn_pipeline)


Results
-------

Finally, we print the pipeline outputs

::

    print "\nOUTPUTS\n"
    for trait_name, trait_value in conn_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)


.. note::
    Since only the motion and eddy corrections has been selected,
    the *unwrapped_phase_file* and *susceptibility_corrected_file*
    are not specified.
    Thus the *corrected_file* output contains the motion-eddy corrected
    image.

