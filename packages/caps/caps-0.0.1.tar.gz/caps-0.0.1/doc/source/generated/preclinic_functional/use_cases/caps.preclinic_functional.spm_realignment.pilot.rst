.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

.. _example_caps.preclinic_functional.spm_realignment.pilot :

Coregistration Tool
    
.. hidden-code-block:: python
    :starthidden: True

    # The full use case code: caps.preclinic_functional.spm_realignment.pilot
    # Pilot imports
    from caps.toy_datasets import get_sample_data
    from capsul.study_config import StudyConfig
    from capsul.utils.sorted_dictionary import SortedDictionary
    from nsap.lib.base import ensure_is_dir

    # Get toy dataset
    toy_dataset = get_sample_data("localizer")

    # Create
    realign_pipeline = Realignment()

    # Print Input Spec
    print realign_pipeline.get_input_spec()

    # Initialize Coregistration pipeline
    realign_pipeline.time_series_image = toy_dataset.fmri

    # Execute the pipeline
    realign_working_dir = os.path.join(working_dir, "realign")
    ensure_is_dir(realign_working_dir)
    default_config = SortedDictionary(
        ("output_directory", realign_working_dir),
        ("spm_directory", "/i2bm/local/spm8"),
        ("matlab_exec", "/neurospin/local/bin/matlab"),
        ("spm_exec_cmd", "/i2bm/local/bin/spm8"),
        ("use_spm_mcr", False),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)
    study.run(realign_pipeline)

    # Print all pipeline outputs
    print "\nOUTPUTS\n"
    for trait_name, trait_value in realign_pipeline.get_outputs().iteritems():
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
    realign_pipeline = Realignment()

    # Print Input Spec
    print realign_pipeline.get_input_spec()

    # Initialize Coregistration pipeline
    realign_pipeline.time_series_image = toy_dataset.fmri

    # Execute the pipeline
    realign_working_dir = os.path.join(working_dir, "realign")
    ensure_is_dir(realign_working_dir)
    default_config = SortedDictionary(
        ("output_directory", realign_working_dir),
        ("spm_directory", "/i2bm/local/spm8"),
        ("matlab_exec", "/neurospin/local/bin/matlab"),
        ("spm_exec_cmd", "/i2bm/local/bin/spm8"),
        ("use_spm_mcr", False),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)
    study.run(realign_pipeline)

    # Print all pipeline outputs
    print "\nOUTPUTS\n"
    for trait_name, trait_value in realign_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)

