.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

.. _example_caps.preclinic_functional.spm_normalization.pilot :

SPM Smoothing Tool
    
.. hidden-code-block:: python
    :starthidden: True

    # The full use case code: caps.preclinic_functional.spm_normalization.pilot
    # Pilot imports
    from capsul.study_config import StudyConfig
    from capsul.utils.sorted_dictionary import SortedDictionary
    from nsap.lib.base import ensure_is_dir
    from caps.toy_datasets import get_sample_data
    
    # Get toy dataset
    toy_dataset = get_sample_data("localizer")

    # Create FSL brain extraction pipeline
    norm_pipeline = Normalization()

    # Print Input Spec
    print norm_pipeline.get_input_spec()

    # Initialize Normalization pipeline
    norm_pipeline.coregistered_struct_image = toy_dataset.mean
    norm_pipeline.func_image = toy_dataset.fmri
    print "SWITCH EVENT"
    norm_pipeline.select_normalization = "segment"
    print (norm_pipeline.nodes["select_normalization"].switch)

    # Execute the pipeline
    norm_working_dir = os.path.join(working_dir, "normalization")
    ensure_is_dir(norm_working_dir)
    default_config = SortedDictionary(
        ("output_directory", norm_working_dir),
        ("spm_directory", "/i2bm/local/spm8-5236"),
        ("matlab_exec", "/neurospin/local/bin/matlab"),
        ("spm_exec_cmd", "/i2bm/local/bin/spm8"),
        ("use_spm_mcr", False),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)
    study.run(norm_pipeline)

    # Print all pipeline outputs
    print "\nOUTPUTS\n"
    for trait_name, trait_value in norm_pipeline.get_outputs().iteritems():
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
    norm_pipeline = Normalization()

    # Print Input Spec
    print norm_pipeline.get_input_spec()

    # Initialize Normalization pipeline
    norm_pipeline.coregistered_struct_image = toy_dataset.mean
    norm_pipeline.func_image = toy_dataset.fmri
    print "SWITCH EVENT"
    norm_pipeline.select_normalization = "segment"
    print (norm_pipeline.nodes["select_normalization"].switch)

    # Execute the pipeline
    norm_working_dir = os.path.join(working_dir, "normalization")
    ensure_is_dir(norm_working_dir)
    default_config = SortedDictionary(
        ("output_directory", norm_working_dir),
        ("spm_directory", "/i2bm/local/spm8-5236"),
        ("matlab_exec", "/neurospin/local/bin/matlab"),
        ("spm_exec_cmd", "/i2bm/local/bin/spm8"),
        ("use_spm_mcr", False),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)
    study.run(norm_pipeline)

    # Print all pipeline outputs
    print "\nOUTPUTS\n"
    for trait_name, trait_value in norm_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)

