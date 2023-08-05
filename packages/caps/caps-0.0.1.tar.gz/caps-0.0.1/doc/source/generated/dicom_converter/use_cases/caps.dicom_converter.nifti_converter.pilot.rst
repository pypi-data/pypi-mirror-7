.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

.. _example_caps.dicom_converter.nifti_converter.pilot :

Coregistration Tool
    
.. hidden-code-block:: python
    :starthidden: True

    # The full use case code: caps.dicom_converter.nifti_converter.pilot
    # Pilot imports
    from caps.toy_datasets import get_sample_data
    from soma.study_config import StudyConfig
    from soma.sorted_dictionary import SortedDictionary
    from nsap.lib.base import ensure_is_dir

    # Get toy dataset
    toy_dataset = get_sample_data("localizer")
    print toy_dataset.anatdcm

    # Create
    nifti_converter_pipeline = Converter_nifti()

    # Print Input Spec
    #print coreg_pipeline.get_input_spec()

    #untar archive
    converter_working_dir = os.path.join(working_dir, "converter")
    ensure_is_dir(converter_working_dir)

    tar_open = tarfile.open(toy_dataset.anatdcm)
    tar_open.extractall(path=os.path.join(converter_working_dir,
                                          "input_data"))
    tar_open.close()

    #get dicom dir
    dicom_dir = os.listdir(os.path.join(converter_working_dir, "input_data"))
    dicom_dir = dicom_dir[0]

    # Initialize pipeline
    nifti_converter_pipeline.dicom_dir = os.path.join(converter_working_dir,
                                                      "input_data", dicom_dir)
    nifti_converter_pipeline.fill_header = False

    # Execute the pipeline
    default_config = SortedDictionary(
        ("output_directory", converter_working_dir),
        ("use_smart_caching", True),
        ("generate_logging", False)
    )
    study = StudyConfig(default_config)
    study.run(nifti_converter_pipeline)

    # Print all pipeline outputs
    print "\nOUTPUTS\n"
    for trait_name, trait_value in nifti_converter_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)


::

    # Pilot imports
    from caps.toy_datasets import get_sample_data
    from soma.study_config import StudyConfig
    from soma.sorted_dictionary import SortedDictionary
    from nsap.lib.base import ensure_is_dir

    # Get toy dataset
    toy_dataset = get_sample_data("localizer")
    print toy_dataset.anatdcm

    # Create
    nifti_converter_pipeline = Converter_nifti()

    # Print Input Spec
    #print coreg_pipeline.get_input_spec()

    #untar archive
    converter_working_dir = os.path.join(working_dir, "converter")
    ensure_is_dir(converter_working_dir)

    tar_open = tarfile.open(toy_dataset.anatdcm)
    tar_open.extractall(path=os.path.join(converter_working_dir,
                                          "input_data"))
    tar_open.close()

    #get dicom dir
    dicom_dir = os.listdir(os.path.join(converter_working_dir, "input_data"))
    dicom_dir = dicom_dir[0]

    # Initialize pipeline
    nifti_converter_pipeline.dicom_dir = os.path.join(converter_working_dir,
                                                      "input_data", dicom_dir)
    nifti_converter_pipeline.fill_header = False

    # Execute the pipeline
    default_config = SortedDictionary(
        ("output_directory", converter_working_dir),
        ("use_smart_caching", True),
        ("generate_logging", False)
    )
    study = StudyConfig(default_config)
    study.run(nifti_converter_pipeline)

    # Print all pipeline outputs
    print "\nOUTPUTS\n"
    for trait_name, trait_value in nifti_converter_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)

