.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

.. _example_caps.preclinic_functional.spm_coregistration.pilot :

Coregistration Tool
    
.. hidden-code-block:: python
    :starthidden: True

    # The full use case code: caps.preclinic_functional.spm_coregistration.pilot
    # Pilot imports
    from caps.toy_datasets import get_sample_data
    from capsul.study_config import StudyConfig
    from capsul.utils.sorted_dictionary import SortedDictionary
    from nsap.lib.base import ensure_is_dir

    # Get toy dataset
    toy_src_dataset = get_sample_data("mni_1mm")
    toy_dest_dataset = get_sample_data("mni_2mm")

    # Create
    coreg_pipeline = Coregistration()

    # Print Input Spec
    print coreg_pipeline.get_input_spec()

    # Initialize Coregistration pipeline
    coreg_pipeline.moving_image = toy_src_dataset.mni
    coreg_pipeline.reference_image = toy_dest_dataset.mni

    # Execute the pipeline
    coreg_working_dir = os.path.join(working_dir, "coregistration")
    ensure_is_dir(coreg_working_dir)
    default_config = SortedDictionary(
        ("output_directory", coreg_working_dir),
        ("spm_directory", "/i2bm/local/spm8"),
        ("matlab_exec", "/neurospin/local/bin/matlab"),
        ("spm_exec_cmd", "/i2bm/local/bin/spm8"),
        ("use_spm_mcr", False),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)
    study.run(coreg_pipeline)

    # Print all pipeline outputs
    print "\nOUTPUTS\n"
    for trait_name, trait_value in coreg_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)


::

    # Pilot imports
    from caps.toy_datasets import get_sample_data
    from capsul.study_config import StudyConfig
    from capsul.utils.sorted_dictionary import SortedDictionary
    from nsap.lib.base import ensure_is_dir

    # Get toy dataset
    toy_src_dataset = get_sample_data("mni_1mm")
    toy_dest_dataset = get_sample_data("mni_2mm")

    # Create
    coreg_pipeline = Coregistration()

    # Print Input Spec
    print coreg_pipeline.get_input_spec()

    # Initialize Coregistration pipeline
    coreg_pipeline.moving_image = toy_src_dataset.mni
    coreg_pipeline.reference_image = toy_dest_dataset.mni

    # Execute the pipeline
    coreg_working_dir = os.path.join(working_dir, "coregistration")
    ensure_is_dir(coreg_working_dir)
    default_config = SortedDictionary(
        ("output_directory", coreg_working_dir),
        ("spm_directory", "/i2bm/local/spm8"),
        ("matlab_exec", "/neurospin/local/bin/matlab"),
        ("spm_exec_cmd", "/i2bm/local/bin/spm8"),
        ("use_spm_mcr", False),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)
    study.run(coreg_pipeline)

    # Print all pipeline outputs
    print "\nOUTPUTS\n"
    for trait_name, trait_value in coreg_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)

