.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

.. _example_caps.preclinic_functional.slice_timing.pilot :

Slice Timing Tool
    
.. hidden-code-block:: python
    :starthidden: True

    # The full use case code: caps.preclinic_functional.slice_timing.pilot
    # Pilot imports
    from caps.toy_datasets import get_sample_data
    from capsul.study_config import StudyConfig
    from capsul.utils.sorted_dictionary import SortedDictionary
    from nsap.lib.base import ensure_is_dir

    # Get toy dataset
    toy_dataset = get_sample_data("localizer")

    # Create
    st_pipeline = SliceTiming()

    # Print Input Spec
    print st_pipeline.get_input_spec()

    # Initialize SliceTiming pipeline
    st_pipeline.fmri_image = toy_dataset.fmri
    st_pipeline.select_slicing = slicing_option
    st_pipeline.force_repetition_time = toy_dataset.TR
    st_pipeline.force_slice_times = list(range(40))

    # Execute the pipeline
    st_working_dir = os.path.join(working_dir, "slice_timing")
    ensure_is_dir(st_working_dir)
    default_config = SortedDictionary(
        ("output_directory", st_working_dir),
        ("fsl_config", "/etc/fsl/4.1/fsl.sh"),
        ("use_fsl", True),
        ("spm_directory", "/i2bm/local/spm8"),
        ("matlab_exec", "/neurospin/local/bin/matlab"),
        ("spm_exec_cmd", "/i2bm/local/bin/spm8"),
        ("use_spm_mcr", False),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)
    study.run(st_pipeline)

    # Print all pipeline outputs
    print "\nOUTPUTS\n"
    for trait_name, trait_value in st_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)


::

    # Pilot imports
    from caps.toy_datasets import get_sample_data
    from capsul.study_config import StudyConfig
    from capsul.utils.sorted_dictionary import SortedDictionary
    from nsap.lib.base import ensure_is_dir

    # Get toy dataset
    toy_dataset = get_sample_data("localizer")

    # Create
    st_pipeline = SliceTiming()

    # Print Input Spec
    print st_pipeline.get_input_spec()

    # Initialize SliceTiming pipeline
    st_pipeline.fmri_image = toy_dataset.fmri
    st_pipeline.select_slicing = slicing_option
    st_pipeline.force_repetition_time = toy_dataset.TR
    st_pipeline.force_slice_times = list(range(40))

    # Execute the pipeline
    st_working_dir = os.path.join(working_dir, "slice_timing")
    ensure_is_dir(st_working_dir)
    default_config = SortedDictionary(
        ("output_directory", st_working_dir),
        ("fsl_config", "/etc/fsl/4.1/fsl.sh"),
        ("use_fsl", True),
        ("spm_directory", "/i2bm/local/spm8"),
        ("matlab_exec", "/neurospin/local/bin/matlab"),
        ("spm_exec_cmd", "/i2bm/local/bin/spm8"),
        ("use_spm_mcr", False),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)
    study.run(st_pipeline)

    # Print all pipeline outputs
    print "\nOUTPUTS\n"
    for trait_name, trait_value in st_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)

