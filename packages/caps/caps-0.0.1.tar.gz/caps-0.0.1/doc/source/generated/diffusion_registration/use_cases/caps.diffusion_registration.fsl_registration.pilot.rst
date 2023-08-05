.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

.. _example_caps.diffusion_registration.fsl_registration.pilot :

==================
FSL FA Registation
==================

.. hidden-code-block:: python
    :starthidden: True

    # The full use case code: caps.diffusion_registration.fsl_registration.pilot
    from caps.toy_datasets import get_sample_data
    from capsul.study_config import StudyConfig
    from capsul.utils.sorted_dictionary import SortedDictionary
    from nsap.lib.base import ensure_is_dir
    import os
    from caps.diffusion_registration.fsl_registration import FSLRegistration
    working_dir = "/volatile/nsap/caps"
    registration_working_dir = os.path.join(working_dir,
                                            "diffusion_registration")
    ensure_is_dir(registration_working_dir)
    default_config = SortedDictionary(
        ("output_directory", registration_working_dir),
        ("fsl_config", "/etc/fsl/4.1/fsl.sh"),
        ("use_fsl", True),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)
    diffusion_dataset = get_sample_data("dwi")
    target_dataset = get_sample_data("fa_1mm")
    print(diffusion_dataset.dwi, diffusion_dataset.bvals,
          diffusion_dataset.bvecs)
    print(target_dataset.template, target_dataset.nl_config)
    registration_pipeline = FSLRegistration()
    print(registration_pipeline.get_input_spec())
    registration_pipeline.fa_file = diffusion_dataset.fa
    registration_pipeline.target_file = target_dataset.template
    registration_pipeline.mask_file = diffusion_dataset.mask
    registration_pipeline.config_file = target_dataset.nl_config
    registration_pipeline.tensor_file = diffusion_dataset.tensor
    study.run(registration_pipeline)
    print("\nOUTPUTS\n")
    outputs = registration_pipeline.get_outputs()
    for trait_name, trait_value in outputs.iteritems():
        print("{0}: {1}".format(trait_name, trait_value))


.. topic:: Objective

    We propose here to register a fractional anisotropy image to a
    reference template and to apply the resulting deformation field
    to the tensor image.

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


We need some generic python modules

::

    import os


From caps we need the pipeline that will enable use to register the
tensor field.

::

    from caps.diffusion_registration.fsl_registration import FSLRegistration


Study Configuration
-------------------

For a complete description of a study configuration, see the
:ref:`Study Configuration description <study_configuration_guide>`

We first define the current working directory

::

    working_dir = "/volatile/nsap/caps"
    registration_working_dir = os.path.join(working_dir,
                                            "diffusion_registration")
    ensure_is_dir(registration_working_dir)


And then define the study configuration.

::

    default_config = SortedDictionary(
        ("output_directory", registration_working_dir),
        ("fsl_config", "/etc/fsl/4.1/fsl.sh"),
        ("use_fsl", True),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)


Load the toy dataset
--------------------

We want to perform a second order tensor fit on a diffusion sequence data.
To do so, we use the *get_sample_data* function to load the diffusion
dataset and the taget template.

.. seealso::

    For a complete description of the *get_sample_data* function, see the
    :ref:`Toy Datasets documentation <toy_datasets_guide>`

::

    diffusion_dataset = get_sample_data("dwi")
    target_dataset = get_sample_data("fa_1mm")


The *diffusion_dataset* is an Enum structure with some specific
elements of interest *dwi*, *bvals*, *bvecs* that contain the nifti
diffusion image ,the b-values and the b-vectors respectively.

::

    print(diffusion_dataset.dwi, diffusion_dataset.bvals,
          diffusion_dataset.bvecs)


Will return:

.. code-block:: python

    /home/ag239446/git/nsap-src/nsap/data/DTI30s010.nii
    /home/ag239446/git/nsap-src/nsap/data/DTI30s010.bval
    /home/ag239446/git/nsap-src/nsap/data/DTI30s010.bvec

We can see that the image has been found in a local directory

The *target_dataset* is an Enum structure with some specific
elements of interest *template*, *nl_config* that contain the fa
diffusion template and the fsl fnirt configuration file.

::

    print(target_dataset.template, target_dataset.nl_config)


Will return:

.. code-block:: python

    /usr/share/fsl/4.1/data/standard/FMRIB58_FA_1mm.nii.gz
    /usr/share/fsl/4.1/etc/flirtsch/FA_2_FMRIB58_1mm.cnf

We can see that the information has been found in the fsl directory.

Processing definition
---------------------

Now we need to define the processing steps that will perform the tensor
registration.

::

    registration_pipeline = FSLRegistration()


It is possible to access the pipeline input specification.

::

    print(registration_pipeline.get_input_spec())


Will return the input parameters the user can set:

.. code-block:: python

    INPUT SPECIFICATIONS

    fa_file: ['File']
    target_file: ['File']
    mask_file: ['File']
    config_file: ['Enum', 'File']

We can now tune the pipeline parameters.

::

    registration_pipeline.fa_file = diffusion_dataset.fa
    registration_pipeline.target_file = target_dataset.template
    registration_pipeline.mask_file = diffusion_dataset.mask
    registration_pipeline.config_file = target_dataset.nl_config
    registration_pipeline.tensor_file = diffusion_dataset.tensor


The pipeline is now ready to be run

::

    study.run(registration_pipeline)


Results
-------

Finally, we print the pipeline outputs

::

    print("\nOUTPUTS\n")
    outputs = registration_pipeline.get_outputs()
    for trait_name, trait_value in outputs.iteritems():
        print("{0}: {1}".format(trait_name, trait_value))


Will return:

.. code-block:: python

    OUTPUTS

