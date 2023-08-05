.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

.. _example_caps.preclinic_functional.spm_preproc.pilot :

SPM Preprocessings
    
.. hidden-code-block:: python
    :starthidden: True

    # The full use case code: caps.preclinic_functional.spm_preproc.pilot
    # Pilot imports
    from capsul.study_config import StudyConfig
    from capsul.utils.sorted_dictionary import SortedDictionary
    from nsap.lib.base import ensure_is_dir
    from caps.toy_datasets import get_sample_data

    # Get toy dataset
    toy_dataset = get_sample_data("localizer")

    # Create FSL brain extraction pipeline
    spm_preproc_pipeline = SPMPreproc()

    # Print Input Spec
    print spm_preproc_pipeline.get_input_spec()

    # Initialize Normalization pipeline
    spm_preproc_pipeline.fmri_image = toy_dataset.fmri
    spm_preproc_pipeline.struct_image = toy_dataset.anat
    spm_preproc_pipeline.select_normalization = "segment"
    spm_preproc_pipeline.select_slicing = "spm"
    spm_preproc_pipeline.force_repetition_time = toy_dataset.TR
    spm_preproc_pipeline.force_slice_times = list(range(40))

    # Execute the pipeline
    spm_preproc_working_dir = os.path.join(working_dir, "spmpreproc")
    ensure_is_dir(spm_preproc_working_dir)
    default_config = SortedDictionary(
        ("output_directory", spm_preproc_working_dir),
        ("fsl_config", "/etc/fsl/4.1/fsl.sh"),
        ("use_fsl", True),
        ("spm_directory", "/i2bm/local/spm8-5236"),
        ("matlab_exec", "/neurospin/local/bin/matlab"),
        ("spm_exec_cmd", "/i2bm/local/bin/spm8"),
        ("use_spm_mcr", False),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)
    study.run(spm_preproc_pipeline)

    # Print all pipeline outputs
    print "\nOUTPUTS\n"
    for trait_name, trait_value in spm_preproc_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)


::

    # Pilot imports
    from capsul.study_config import StudyConfig
    from capsul.utils.sorted_dictionary import SortedDictionary
    from nsap.lib.base import ensure_is_dir
    from caps.toy_datasets import get_sample_data

    # Get toy dataset
    toy_dataset = get_sample_data("localizer")

    # Create FSL brain extraction pipeline
    spm_preproc_pipeline = SPMPreproc()

    # Print Input Spec
    print spm_preproc_pipeline.get_input_spec()

    # Initialize Normalization pipeline
    spm_preproc_pipeline.fmri_image = toy_dataset.fmri
    spm_preproc_pipeline.struct_image = toy_dataset.anat
    spm_preproc_pipeline.select_normalization = "segment"
    spm_preproc_pipeline.select_slicing = "spm"
    spm_preproc_pipeline.force_repetition_time = toy_dataset.TR
    spm_preproc_pipeline.force_slice_times = list(range(40))

    # Execute the pipeline
    spm_preproc_working_dir = os.path.join(working_dir, "spmpreproc")
    ensure_is_dir(spm_preproc_working_dir)
    default_config = SortedDictionary(
        ("output_directory", spm_preproc_working_dir),
        ("fsl_config", "/etc/fsl/4.1/fsl.sh"),
        ("use_fsl", True),
        ("spm_directory", "/i2bm/local/spm8-5236"),
        ("matlab_exec", "/neurospin/local/bin/matlab"),
        ("spm_exec_cmd", "/i2bm/local/bin/spm8"),
        ("use_spm_mcr", False),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)
    study.run(spm_preproc_pipeline)

    # Print all pipeline outputs
    print "\nOUTPUTS\n"
    for trait_name, trait_value in spm_preproc_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)

