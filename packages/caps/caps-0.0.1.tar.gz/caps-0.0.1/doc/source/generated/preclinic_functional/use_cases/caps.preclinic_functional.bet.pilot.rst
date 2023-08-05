.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

.. _example_caps.preclinic_functional.bet.pilot :

FSL Brain Extraction Tool
    
.. hidden-code-block:: python
    :starthidden: True

    # The full use case code: caps.preclinic_functional.bet.pilot
    # Pilot imports
    from caps.toy_datasets import get_sample_data
    from capsul.study_config import StudyConfig
    from capsul.utils.sorted_dictionary import SortedDictionary
    from nsap.lib.base import ensure_is_dir

    # Get toy dataset
    toy_dataset = get_sample_data("mni_2mm")

    # Create FSL brain extraction pipeline
    bet_pipeline = BET()

    # Print Input Spec
    print bet_pipeline.get_input_spec()

    # Initialize BET pipeline
    bet_pipeline.input_file = toy_dataset.mni

    # Execute the pipeline
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

    # Print all pipeline outputs
    print "\nOUTPUTS\n"
    for trait_name, trait_value in bet_pipeline.get_outputs().iteritems():
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
    bet_pipeline = BET()

    # Print Input Spec
    print bet_pipeline.get_input_spec()

    # Initialize BET pipeline
    bet_pipeline.input_file = toy_dataset.mni

    # Execute the pipeline
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

    # Print all pipeline outputs
    print "\nOUTPUTS\n"
    for trait_name, trait_value in bet_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)

