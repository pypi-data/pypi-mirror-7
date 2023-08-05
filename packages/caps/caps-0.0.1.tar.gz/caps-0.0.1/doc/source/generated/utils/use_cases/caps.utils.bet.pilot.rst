.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

.. _example_caps.utils.bet.pilot :

=========================
FSL Brain Extraction Tool
=========================

.. hidden-code-block:: python
    :starthidden: True

    # The full use case code: caps.utils.bet.pilot
    from caps.toy_datasets import get_sample_data
    from capsul.study_config import StudyConfig
    from capsul.utils.sorted_dictionary import SortedDictionary
    from nsap.lib.base import ensure_is_dir
    toy_dataset = get_sample_data("mni_2mm")
    print(toy_dataset.mni)
    bet_pipeline = BET()
    print(bet_pipeline.get_input_spec())
    bet_pipeline.input_file = toy_dataset.mni
    bet_pipeline.bet_threshold = 0.5
    bet_working_dir = os.path.join(working_dir, "bet")
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


Small introduction
------------------

FSL Brain Extraction Tool (BET) deletes non-brain tissue
from an image of the whole head. It can also estimate the inner
and outer skull surfaces, and outer scalp surface,
if you have good quality T1 and T2 input images.

.. topic:: Objective

    We propose to extract the brain mask only of a T2 wheighted image.

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

We want to perform BET on the 2mm MNI template.
To do so, we use the *get_sample_data* function to load this
template.

.. seealso::

    For a complete description of the *get_sample_data* function, see the
    :ref:`Toy Datasets documentation <toy_datasets_guide>`

::

    toy_dataset = get_sample_data("mni_2mm")


The *toy_dataset* is an Enum structure with one specific
element of interest *mni* that contains the nifti 2 mm MNI image.

::

    print(toy_dataset.mni)


Will return:

.. code-block:: python

    /usr/share/fsl/4.1/data/standard/MNI152_T1_2mm.nii.gz

We can see that the image has been found in the FSL library

Processing definition
---------------------

Now we need to define the processing step that will perform BET

::

    bet_pipeline = BET()


It is possible to access the ipeline input specification.

::

    print(bet_pipeline.get_input_spec())


Will return the input parameters the user can set:

.. code-block:: python

    INPUT SPECIFICATIONS

    input_file: ['File']
    generate_binary_mask: ['Bool']
    use_4d_input: ['Bool']
    generate_mesh: ['Bool']
    generate_skull: ['Bool']
    bet_threshold: ['Float']

.. seealso::
    For a complete description of the API, see the
    :ref:`BET API description <caps.utils.bet.BET>`

We can now tune the pipeline parameters.
We first set the input file:

::

    bet_pipeline.input_file = toy_dataset.mni


And set the BET stoping criterion: this value belong to to the [0, 1]
iterval. When the fractional intensity threshold increase,
the generated mask will be more constrained.

::

    bet_pipeline.bet_threshold = 0.5


Study Configuration
-------------------

The pipeline is now set up and ready to be executed.
For a complete description of a study execution, see the
:ref:`Study Configuration description <study_configuration_guide>`

::

    bet_working_dir = os.path.join(working_dir, "bet")
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


Will return all the output parameters the user can access:

.. code-block:: python

    OUTPUTS

    bet_skull_mask_file: <undefined>
    bet_outskin_mask_file: <undefined>
    bet_meshfile: <undefined>
    bet_inskull_mask_file: <undefined>
    bet_outskull_mask_file: <undefined>
    bet_inskull_mesh_file: <undefined>
    bet_mask_file: <undefined>
    bet_outskin_mesh_file: <undefined>
    bet_out_file: /volatile/nsap/caps/bet/1-bet/MNI152_T1_2mm_brain.nii.gz
    bet_outskull_mesh_file: <undefined>

.. note::
    Since only the brain has been requested, all the other outputs
    are set to None.
    Only the *bet_out_file* output is of interest for this study.

