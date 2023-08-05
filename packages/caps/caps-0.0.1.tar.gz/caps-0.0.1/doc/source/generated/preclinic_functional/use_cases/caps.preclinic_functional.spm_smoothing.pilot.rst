.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

.. _example_caps.preclinic_functional.spm_smoothing.pilot :

SPM Smoothing Tool
    
.. hidden-code-block:: python
    :starthidden: True

    # The full use case code: caps.preclinic_functional.spm_smoothing.pilot
    # Pilot imports
    from caps.toy_datasets import get_sample_data
    from capsul.study_config import StudyConfig
    from capsul.utils.sorted_dictionary import SortedDictionary
    from nsap.lib.base import ensure_is_dir

    # Get toy dataset
    toy_dataset = get_sample_data("mni_2mm")

    # Create FSL brain extraction pipeline
    smooth_pipeline = Smoothing()

    # Print Input Spec
    print smooth_pipeline.get_input_spec()

    # Initialize Smoothing pipeline
    smooth_pipeline.input_image = toy_dataset.mni

    # Execute the pipeline
    smooth_working_dir = os.path.join(working_dir, "smoothing")
    ensure_is_dir(smooth_working_dir)
    default_config = SortedDictionary(
        ("output_directory", smooth_working_dir),
        ("spm_directory", "/i2bm/local/spm8-5236"),
        ("matlab_exec", "/neurospin/local/bin/matlab"),
        ("spm_exec_cmd", "/i2bm/local/bin/spm8"),
        ("use_spm_mcr", False),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)
    study.run(smooth_pipeline)

    # Print all pipeline outputs
    print "\nOUTPUTS\n"
    for trait_name, trait_value in smooth_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)


::

    # Pilot imports
    from caps.toy_datasets import get_sample_data
    from capsul.study_config import StudyConfig
    from capsul.utils.sorted_dictionary import SortedDictionary
    from nsap.lib.base import ensure_is_dir

    # Get toy dataset
    toy_dataset = get_sample_data("mni_2mm")

    # Create FSL brain extraction pipeline
    smooth_pipeline = Smoothing()

    # Print Input Spec
    print smooth_pipeline.get_input_spec()

    # Initialize Smoothing pipeline
    smooth_pipeline.input_image = toy_dataset.mni

    # Execute the pipeline
    smooth_working_dir = os.path.join(working_dir, "smoothing")
    ensure_is_dir(smooth_working_dir)
    default_config = SortedDictionary(
        ("output_directory", smooth_working_dir),
        ("spm_directory", "/i2bm/local/spm8-5236"),
        ("matlab_exec", "/neurospin/local/bin/matlab"),
        ("spm_exec_cmd", "/i2bm/local/bin/spm8"),
        ("use_spm_mcr", False),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)
    study.run(smooth_pipeline)

    # Print all pipeline outputs
    print "\nOUTPUTS\n"
    for trait_name, trait_value in smooth_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)

