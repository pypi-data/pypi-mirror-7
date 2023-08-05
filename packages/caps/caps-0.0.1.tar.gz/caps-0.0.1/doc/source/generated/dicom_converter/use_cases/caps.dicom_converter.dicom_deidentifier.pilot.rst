.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

.. _example_caps.dicom_converter.dicom_deidentifier.pilot :

Dicom anonymizer tool
    
.. hidden-code-block:: python
    :starthidden: True

    # The full use case code: caps.dicom_converter.dicom_deidentifier.pilot
    from capsul.study_config import StudyConfig
    from capsul.utils.sorted_dictionary import SortedDictionary

    # Create
    dicom_anonymizer_pipeline = Dicom_anonymiser()

    # Initialize pipeline
    dicom_anonymizer_pipeline.select_ano = "ano"
    dicom_anonymizer_pipeline.dicom_dir = "/volatile/TEST/DICOM"
    dicom_anonymizer_pipeline.psc1 = "060000125528"
    dicom_anonymizer_pipeline.no_dicom_marker = True
    dicom_anonymizer_pipeline.remove_curves = True
    dicom_anonymizer_pipeline.remove_private_tags = True
    dicom_anonymizer_pipeline.remove_overlays = True
    dicom_anonymizer_pipeline.fill_public_diffusion_tags = True
    dicom_anonymizer_pipeline.use_sop_instance_uid = False
    dicom_anonymizer_pipeline.root_folder = "/volatile/TEST/output_test"
    dicom_anonymizer_pipeline.save_de_identification_footprints = False
    dicom_anonymizer_pipeline.split_series = False

    ensure_is_dir(os.path.join(working_dir, "de_identifier"))
    # Execute the pipeline
    default_config = SortedDictionary(
        ("output_directory", os.path.join(working_dir, "de_identifier")),
        ("use_smart_caching", False),
        ("generate_logging", False)
    )
    study = StudyConfig(default_config)
    study.run(dicom_anonymizer_pipeline)

    # Print all pipeline outputs
    print "\nOUTPUTS\n"
    for trait_name, trait_value in dicom_anonymizer_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)


::

    from capsul.study_config import StudyConfig
    from capsul.utils.sorted_dictionary import SortedDictionary

    # Create
    dicom_anonymizer_pipeline = Dicom_anonymiser()

    # Initialize pipeline
    dicom_anonymizer_pipeline.select_ano = "ano"
    dicom_anonymizer_pipeline.dicom_dir = "/volatile/TEST/DICOM"
    dicom_anonymizer_pipeline.psc1 = "060000125528"
    dicom_anonymizer_pipeline.no_dicom_marker = True
    dicom_anonymizer_pipeline.remove_curves = True
    dicom_anonymizer_pipeline.remove_private_tags = True
    dicom_anonymizer_pipeline.remove_overlays = True
    dicom_anonymizer_pipeline.fill_public_diffusion_tags = True
    dicom_anonymizer_pipeline.use_sop_instance_uid = False
    dicom_anonymizer_pipeline.root_folder = "/volatile/TEST/output_test"
    dicom_anonymizer_pipeline.save_de_identification_footprints = False
    dicom_anonymizer_pipeline.split_series = False

    ensure_is_dir(os.path.join(working_dir, "de_identifier"))
    # Execute the pipeline
    default_config = SortedDictionary(
        ("output_directory", os.path.join(working_dir, "de_identifier")),
        ("use_smart_caching", False),
        ("generate_logging", False)
    )
    study = StudyConfig(default_config)
    study.run(dicom_anonymizer_pipeline)

    # Print all pipeline outputs
    print "\nOUTPUTS\n"
    for trait_name, trait_value in dicom_anonymizer_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)

