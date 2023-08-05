.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

.. _example_caps.quality_control.snapshots.pilot :

============================
FSL diffusion preprocessings
============================

.. hidden-code-block:: python
    :starthidden: True

    # The full use case code: caps.quality_control.snapshots.pilot
    from caps.toy_datasets import get_sample_data
    from capsul.study_config import StudyConfig
    from capsul.utils.sorted_dictionary import SortedDictionary
    from caps.dicom_converter.base.tools import ensure_is_dir
    toy_dataset = get_sample_data("mni_2mm")
    print(toy_dataset.mni, toy_dataset.mask)
    snap_pipeline = Snap()
    print(snap_pipeline.get_input_spec())
    snap_pipeline.switch_QC = "MULTI"

    snap_pipeline.input_image = toy_dataset.mni
    snap_pipeline.lower_bound = 0.15
    snap_pipeline.upper_bound = 0.85
    snap_pipeline.nb_steps = 6
    snap_pipeline.edges_image = toy_dataset.mask
    """
    Study Configuration
    -------------------

    The pipeline is now set up and ready to be executed.
    For a complete description of a study execution, see the
    :ref:`Study Configuration description <study_configuration_guide>`    snap_working_dir = os.path.join(working_dir, "snap")
    ensure_is_dir(snap_working_dir)
    default_config = SortedDictionary(
        ("output_directory", snap_working_dir),
        ("fsl_config", "/etc/fsl/4.1/fsl.sh"),
        ("use_fsl", True),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)
    study.run(snap_pipeline)
    print "\nOUTPUTS\n"
    for trait_name, trait_value in \
                        snap_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)


.. topic:: Objective

    We propose to make a quality control of a diffusion sequence:
    Simple snapshot (SCA)
    Multi snapshot, more complete (MULTI)

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

We want to perform Snap on a diffusion sequence.
To do so, we use the *get_sample_data* function to load this
dataset.

.. seealso::

    For a complete description of the *get_sample_data* function, see the
    :ref:`Toy Datasets documentation <toy_datasets_guide>`

::

    toy_dataset = get_sample_data("mni_2mm")


The *toy_dataset* is an Enum structure with some specific
elements of interest *dwi*, *bvals*, *bvecs* that contain the nifti
diffusion image ,the b-values and the b-vectors respectively.

::

    print(toy_dataset.mni, toy_dataset.mask)


Will return:

.. code-block:: python

    /home/.../git/nsap-src/nsap/data/DTI30s010.nii
    /home/.../git/nsap-src/nsap/data/DTI30s010.bval
    /home/.../git/nsap-src/nsap/data/DTI30s010.bvec

We can see that the image has been found in a local directory

Processing definition
---------------------

Now we need to define the processing step that will perform the diffusion
preprocessings.

::

    snap_pipeline = Snap()


It is possible to access the pipeline input specification.

::

    print(snap_pipeline.get_input_spec())


Will return the input parameters the user can set:

.. code-block:: python

    INPUT SPECIFICATIONS

    switch_mode: ['Enum']
    lower_bound: ['Float']
    upper_bound: ['Float']
    nb_steps: ['Int']
    output_dir: ['Directory']
    target: ['File']
    edges_image: ['File']
    input_image: ['File']


We activate the multi snap path

::

    snap_pipeline.switch_QC = "MULTI"


We can now tune the pipeline parameters.
We first set the input dwi file:

::


    snap_pipeline.input_image = toy_dataset.mni
    snap_pipeline.lower_bound = 0.15
    snap_pipeline.upper_bound = 0.85
    snap_pipeline.nb_steps = 6
    snap_pipeline.edges_image = toy_dataset.mask
    """
    Study Configuration
    -------------------

    The pipeline is now set up and ready to be executed.
    For a complete description of a study execution, see the
    :ref:`Study Configuration description <study_configuration_guide>`

Study Configuration
-------------------

The pipeline is now set up and ready to be executed.
For a complete description of a study execution, see the
:ref:`Study Configuration description <study_configuration_guide>`

::

    snap_working_dir = os.path.join(working_dir, "snap")
    ensure_is_dir(snap_working_dir)
    default_config = SortedDictionary(
        ("output_directory", snap_working_dir),
        ("fsl_config", "/etc/fsl/4.1/fsl.sh"),
        ("use_fsl", True),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)
    study.run(snap_pipeline)


Results
-------

Finally, we print the pipeline outputs

::

    print "\nOUTPUTS\n"
    for trait_name, trait_value in \
                        snap_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)


.. note::
    Since only the motion and eddy corrections has been selected,
    the *unwrapped_phase_file* and *susceptibility_corrected_file*
    are not specified.
    Thus the *corrected_file* output contains the motion-eddy corrected
    image.

