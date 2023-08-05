.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

.. _example_caps.diffusion_preproc.fsl_preproc.pilot :

============================
FSL diffusion preprocessings
============================

.. hidden-code-block:: python
    :starthidden: True

    # The full use case code: caps.diffusion_preproc.fsl_preproc.pilot
    from caps.toy_datasets import get_sample_data
    from capsul.study_config import StudyConfig
    from capsul.utils.sorted_dictionary import SortedDictionary
    from caps.dicom_converter.base.tools import ensure_is_dir
    toy_dataset = get_sample_data("dwi")
    print(toy_dataset.dwi, toy_dataset.bvals, toy_dataset.bvecs)
    fsl_preproc_pipeline = FslDiffsuionPpreprocessings()
    print(fsl_preproc_pipeline.get_input_spec())
    fsl_preproc_pipeline.dw_image = toy_dataset.dwi
    fsl_preproc_pipeline.bvals = toy_dataset.bvals
    fsl_preproc_pipeline.bvecs = toy_dataset.bvecs
    fsl_preproc_pipeline.do_motion_correction = "YES"
    fsl_preproc_pipeline.do_susceptibility_correction = "YES"
    preproc_working_dir = os.path.join(working_dir, "fsl_preproc")
    ensure_is_dir(preproc_working_dir)
    default_config = SortedDictionary(
        ("output_directory", preproc_working_dir),
        ("fsl_config", "/etc/fsl/4.1/fsl.sh"),
        ("use_fsl", True),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)
    study.run(fsl_preproc_pipeline)
    print "\nOUTPUTS\n"
    for trait_name, trait_value in \
                        fsl_preproc_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)


.. topic:: Objective

    We propose to correct some distortion of a diffusion sequence:
    Motion Correction - Eddy Currents Correction -
    Susceptibility Artifacts Correction (not tested yet)

Import
------

First we load the function that enables us to access the toy datasets

::

    from caps.toy_datasets import get_sample_data


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


Load the toy dataset
--------------------

We want to perform BET on a diffusion sequence.
To do so, we use the *get_sample_data* function to load this
dataset.

.. seealso::

    For a complete description of the *get_sample_data* function, see the
    :ref:`Toy Datasets documentation <toy_datasets_guide>`

::

    toy_dataset = get_sample_data("dwi")


The *toy_dataset* is an Enum structure with some specific
elements of interest *dwi*, *bvals*, *bvecs* that contain the nifti
diffusion image ,the b-values and the b-vectors respectively.

::

    print(toy_dataset.dwi, toy_dataset.bvals, toy_dataset.bvecs)


Will return:

.. code-block:: python

    /home/ag239446/git/nsap-src/nsap/data/DTI30s010.nii
    /home/ag239446/git/nsap-src/nsap/data/DTI30s010.bval
    /home/ag239446/git/nsap-src/nsap/data/DTI30s010.bvec

We can see that the image has been found in a local directory

Processing definition
---------------------

Now we need to define the processing step that will perform the diffusion
preprocessings.

::

    fsl_preproc_pipeline = FslDiffsuionPpreprocessings()


It is possible to access the ipeline input specification.

::

    print(fsl_preproc_pipeline.get_input_spec())


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

    preproc_working_dir = os.path.join(working_dir, "fsl_preproc")
    ensure_is_dir(preproc_working_dir)
    default_config = SortedDictionary(
        ("output_directory", preproc_working_dir),
        ("fsl_config", "/etc/fsl/4.1/fsl.sh"),
        ("use_fsl", True),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)
    study.run(fsl_preproc_pipeline)


Results
-------

Finally, we print the pipeline outputs

::

    print "\nOUTPUTS\n"
    for trait_name, trait_value in \
                        fsl_preproc_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)


.. note::
    Since only the motion and eddy corrections has been selected,
    the *unwrapped_phase_file* and *susceptibility_corrected_file*
    are not specified.
    Thus the *corrected_file* output contains the motion-eddy corrected
    image.

