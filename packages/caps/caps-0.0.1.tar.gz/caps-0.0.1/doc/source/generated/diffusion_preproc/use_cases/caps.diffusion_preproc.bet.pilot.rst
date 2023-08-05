.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

.. _example_caps.diffusion_preproc.bet.pilot :

===============================
Diffusion Brain Extraction Tool
===============================

.. hidden-code-block:: python
    :starthidden: True

    # The full use case code: caps.diffusion_preproc.bet.pilot
    from caps.toy_datasets import get_sample_data
    from capsul.study_config import StudyConfig
    from capsul.utils.sorted_dictionary import SortedDictionary
    from nsap.lib.base import ensure_is_dir
    toy_dataset = get_sample_data("dwi")
    print(toy_dataset.dwi, toy_dataset.bvals)
    bet_pipeline = dBET()
    print(bet_pipeline.get_input_spec())
    bet_pipeline.dw_image = toy_dataset.dwi
    bet_pipeline.bvals = toy_dataset.bvals
    bet_working_dir = os.path.join(working_dir, "diffusion_bet")
    ensure_is_dir(bet_working_dir)
    default_config = SortedDictionary(
        ("output_directory", bet_working_dir),
        ("fsl_config", "/etc/fsl/4.1/fsl.sh"),
        ("use_fsl", True),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)
    study.run(bet_pipeline)
    print("\nOUTPUTS\n")
    for trait_name, trait_value in bet_pipeline.get_outputs().iteritems():
        print("{0}: {1}".format(trait_name, trait_value))

.. topic:: Objective

    We propose to extract the brain mask from a diffusion sequence.

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
    from nsap.lib.base import ensure_is_dir


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
elements of interest *dwi*, *bvals* that contain the nifti diffusion
image and the b-values respectively.

::

    print(toy_dataset.dwi, toy_dataset.bvals)


Will return:

.. code-block:: python

    /home/ag239446/git/nsap-src/nsap/data/DTI30s010.nii
    /home/ag239446/git/nsap-src/nsap/data/DTI30s010.bval

We can see that the image has been found in a local directory

Processing definition
---------------------

Now we need to define the processing step that will perform BET on
diffusion sequence.

::

    bet_pipeline = dBET()


It is possible to access the ipeline input specification.

::

    print(bet_pipeline.get_input_spec())


Will return the input parameters the user can set:

.. code-block:: python

    INPUT SPECIFICATIONS

    dw_image: ['File']
    bvals: ['File']
    specified_index_of_ref_image: ['Int']
    terminal_output: ['Enum']
    generate_binary_mask: ['Bool']
    use_4d_input: ['Bool']
    generate_mesh: ['Bool']
    generate_skull: ['Bool']
    bet_threshold: ['Float']

We can now tune the pipeline parameters.
We first set the input dwi file:

::

    bet_pipeline.dw_image = toy_dataset.dwi


And set the b-values file

::

    bet_pipeline.bvals = toy_dataset.bvals


Study Configuration
-------------------

The pipeline is now set up and ready to be executed.
For a complete description of a study execution, see the
:ref:`Study Configuration description <study_configuration_guide>`

::

    bet_working_dir = os.path.join(working_dir, "diffusion_bet")
    ensure_is_dir(bet_working_dir)
    default_config = SortedDictionary(
        ("output_directory", bet_working_dir),
        ("fsl_config", "/etc/fsl/4.1/fsl.sh"),
        ("use_fsl", True),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)
    study.run(bet_pipeline)


Results
-------

Finally, we print the pipeline outputs

::

    print("\nOUTPUTS\n")
    for trait_name, trait_value in bet_pipeline.get_outputs().iteritems():
        print("{0}: {1}".format(trait_name, trait_value))


.. note::
    Since only the brain mask has been requested, all the other outputs
    are set to None.
    Only the *bet_out_file*, *splited_images*, *bet_mask_file*,
    *ref_image*, *index_of_ref_image* outputs are of interest for
    this study.

