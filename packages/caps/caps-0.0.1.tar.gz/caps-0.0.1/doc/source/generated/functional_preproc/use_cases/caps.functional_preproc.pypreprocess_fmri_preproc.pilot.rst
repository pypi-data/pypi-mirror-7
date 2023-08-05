.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

.. _example_caps.functional_preproc.pypreprocess_fmri_preproc.pilot :

==================================
Functional Spatial Preprocessings
==================================

.. hidden-code-block:: python
    :starthidden: True

    # The full use case code: caps.functional_preproc.pypreprocess_fmri_preproc.pilot
    from caps.toy_datasets import get_sample_data
    from capsul.study_config import StudyConfig
    from capsul.utils.sorted_dictionary import SortedDictionary
    from nsap.lib.base import ensure_is_dir
    import os
    import numpy
    from caps.functional_preproc.pypreprocess_fmri_preproc import (
        SPMSubjectPreprocessing)
    working_dir = "/volatile/nsap/caps"
    preproc_working_dir = os.path.join(working_dir, "functional_preroc")
    ensure_is_dir(preproc_working_dir)
    default_config = SortedDictionary(
        ("output_directory", preproc_working_dir),
        ("spm_directory", "/i2bm/local/spm8-5236"),
        ("matlab_exec", "/neurospin/local/bin/matlab"),
        ("spm_exec_cmd", "/i2bm/local/bin/spm8"),
        ("use_spm_mcr", False),
        ("use_smart_caching", False),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)
    toy_dataset = get_sample_data("localizer")
    timings = list(range(1, 41))
    print(toy_dataset.fmri, toy_dataset.anat, toy_dataset.TR, timings)
    preproc_pipeline = SPMSubjectPreprocessing()
    print(preproc_pipeline.get_input_spec())
    preproc_pipeline.func_file = toy_dataset.fmri
    preproc_pipeline.anat_file = toy_dataset.anat
    preproc_pipeline.repetition_time = toy_dataset.TR
    preproc_pipeline.slice_order = timings
    preproc_pipeline.fwhm = [5, 5, 5]
    preproc_pipeline.coreg_anat_to_func = False
    preproc_pipeline.slice_time = True
    preproc_pipeline.realign = True
    preproc_pipeline.coregister = True
    preproc_pipeline.segment = True
    preproc_pipeline.normalize = True
    preproc_pipeline.use_smart_caching = True
    study.run(preproc_pipeline)
    print("\nOUTPUTS\n")
    for trait_name, trait_value in preproc_pipeline.get_outputs().iteritems():
        print("{0}: {1}".format(trait_name, trait_value))

.. topic:: Objective

    We propose here to spatialy correct functional images using
    PyPreProcess (SPM).

Import
------

First we load the function that enables us to access the toy datasets:

::

    from caps.toy_datasets import get_sample_data


From capsul we then load the class to configure the study we want to
perform:

::

    from capsul.study_config import StudyConfig


Here two utility tools are loaded. The first one enables the creation
of ordered dictionary and the second ensure that a directory exists.
Note that the directory will be created if necessary.

::

    from capsul.utils.sorted_dictionary import SortedDictionary
    from nsap.lib.base import ensure_is_dir


We need some generic python modules:

::

    import os
    import numpy


From caps we need the pipeline that will enable use to do the functional
spatial preprocessings:

::

    from caps.functional_preproc.pypreprocess_fmri_preproc import (
        SPMSubjectPreprocessing)


Study Configuration
-------------------

For a complete description of a study configuration, see the
:ref:`Study Configuration description <study_configuration_guide>`

We first define the current working directory:

::

    working_dir = "/volatile/nsap/caps"
    preproc_working_dir = os.path.join(working_dir, "functional_preroc")
    ensure_is_dir(preproc_working_dir)


And then define the study configuration:

::

    default_config = SortedDictionary(
        ("output_directory", preproc_working_dir),
        ("spm_directory", "/i2bm/local/spm8-5236"),
        ("matlab_exec", "/neurospin/local/bin/matlab"),
        ("spm_exec_cmd", "/i2bm/local/bin/spm8"),
        ("use_spm_mcr", False),
        ("use_smart_caching", False),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)


Load the toy dataset
--------------------

We want to perform a second order tensor fit on a diffusion sequence data.
To do so, we use the *get_sample_data* function to load the
dataset:

.. seealso::

    For a complete description of the *get_sample_data* function, see the
    :ref:`Toy Datasets documentation <toy_datasets_guide>`

::

    toy_dataset = get_sample_data("localizer")


The *toy_dataset* is an Enum structure with some specific
elements of interest *fmri*, *anat*, *TR* that contains
the nifti functional image, the nifti anatomical image,
and the repetition time respectively.

::

    timings = list(range(1, 41))
    print(toy_dataset.fmri, toy_dataset.anat, toy_dataset.TR, timings)


Processing definition
---------------------

Now we need to define the processing step that will perform the
functional spatial preprocessings:

::

    preproc_pipeline = SPMSubjectPreprocessing()


It is possible to access the pipeline input specifications:

::

    print(preproc_pipeline.get_input_spec())


Will return the input parameters the user can set:

.. code-block:: python

    INPUT SPECIFICATIONS

    func_file: ['File']
    anat_file: ['File']
    output_directory: ['Directory']
    slice_time: ['Bool']
    realign: ['Bool']
    coregister: ['Bool']
    coreg_anat_to_func: ['Bool']
    segment: ['Bool']
    normalize: ['Bool']
    fwhm: ['List_Float', 'Float', 'TraitInstance']
    repetition_tile: ['Float']
    slice_order: ['List_Int']

We can now tune the pipeline parameters:

::

    preproc_pipeline.func_file = toy_dataset.fmri
    preproc_pipeline.anat_file = toy_dataset.anat
    preproc_pipeline.repetition_time = toy_dataset.TR
    preproc_pipeline.slice_order = timings
    preproc_pipeline.fwhm = [5, 5, 5]
    preproc_pipeline.coreg_anat_to_func = False


Before running the pipeline, you need to select the spatial preproc that
will be performed:

::

    preproc_pipeline.slice_time = True
    preproc_pipeline.realign = True
    preproc_pipeline.coregister = True
    preproc_pipeline.segment = True
    preproc_pipeline.normalize = True


You can also specify that you want to activate nipype smart-caching

::

    preproc_pipeline.use_smart_caching = True


The pipeline is now ready to be run

::

    study.run(preproc_pipeline)


Results
-------

Finally, we print the pipeline outputs

::

    print("\nOUTPUTS\n")
    for trait_name, trait_value in preproc_pipeline.get_outputs().iteritems():
        print("{0}: {1}".format(trait_name, trait_value))

