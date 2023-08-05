.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

.. _example_caps.quality_control.brainvisa_map_cluster_analysis.pilot :

============================
FSL diffusion preprocessings
============================

.. hidden-code-block:: python
    :starthidden: True

    # The full use case code: caps.quality_control.brainvisa_map_cluster_analysis.pilot
    import subprocess
    from capsul.study_config import StudyConfig
    from capsul.utils.sorted_dictionary import SortedDictionary
    from caps.dicom_converter.base.tools import ensure_is_dir
    wmap = get_sample_data("tpm").wm
    reference = get_sample_data("tpm").gm
    """
    The *toy_dataset* is an Enum structure with some specific
    elements of interest *dwi*, *bvals*, *bvecs* that contain the nifti
    diffusion image ,the b-values and the b-vectors respectively.    print(wmap, reference)
    map_cluster_analysis_pipeline = MapClusterAnalysis()
    print(map_cluster_analysis_pipeline.get_input_spec())
    map_cluster_analysis_pipeline.map_image = wmap
    map_cluster_analysis_pipeline.thresh_size = 10
    map_cluster_analysis_pipeline.thresh_neg_bound = (-np.inf, -3)
    map_cluster_analysis_pipeline.thresh_pos_bound = (0.8, np.inf)
    map_cluster_analysis_pipeline.reference_image = reference
    """
    Study Configuration
    -------------------

    The pipeline is now set up and ready to be executed.
    For a complete description of a study execution, see the
    :ref:`Study Configuration description <study_configuration_guide>`    brain_working_dir = os.path.join(working_dir, "brain")
    ensure_is_dir(brain_working_dir)
    default_config = SortedDictionary(
        ("output_directory", brain_working_dir),
        ("fsl_config", "/etc/fsl/4.1/fsl.sh"),
        ("use_fsl", True),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)
    study.run(map_cluster_analysis_pipeline)
    print "\nOUTPUTS\n"
    for trait_name, trait_value in \
                    map_cluster_analysis_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)
    viewer_node = map_cluster_analysis_pipeline.nodes["mesh_cluster_rendering"]
    viewer_process = viewer_node.process
    for plug_name, plug in viewer_node.plugs.iteritems():
        if plug_name in ["nodes_activation", "selection_changed"]:
            continue
        # since it is a viewer node we normally have only inputs
        for (source_node_name, source_plug_name, source_node,
            source_plug, weak_link) in plug.links_from:

            source_plug_value = getattr(source_node.process,
                                        source_plug_name)
            source_trait = source_node.process.trait(source_plug_name)
            setattr(viewer_process, plug_name, source_plug_value)
    subprocess.Popen(viewer_process.get_commandline())

.. topic:: Objective

    We propose to make a quality control of a diffusion sequence:
    Mesh Clusters in MNI space.

Import
------

First we load the function that enables us to access the toy datasets

::

    import subprocess


From capsul we then load the class to configure the study we want to
perform

::

    from capsul.study_config import StudyConfig


Here two utility tools are loaded. The first one enables the creation
of ordered dictionary and the second ensure that a directory exist.
Note that the directory will be created if necessary.

::

    from capsul.utils.sorted_dictionary import SortedDictionary
    from caps.dicom_converter.base.tools import ensure_is_dir


Load the toy dataset
--------------------

We want to perform Snap on a diffusion sequence.
To do so, we use the *get_sample_data* function to load this
dataset.

.. seealso::

    For a complete description of the *get_sample_data* function, see the
    :ref:`Toy Datasets documentation <toy_datasets_guide>`

::

    wmap = get_sample_data("tpm").wm
    reference = get_sample_data("tpm").gm
    """
    The *toy_dataset* is an Enum structure with some specific
    elements of interest *dwi*, *bvals*, *bvecs* that contain the nifti
    diffusion image ,the b-values and the b-vectors respectively.

The *toy_dataset* is an Enum structure with some specific
elements of interest *dwi*, *bvals*, *bvecs* that contain the nifti
diffusion image ,the b-values and the b-vectors respectively.

::

    print(wmap, reference)


Will return:

.. code-block:: python

    /i2bm/local/spm8-5236/tpm/white.nii
    /i2bm/local/spm8-5236/tpm/grey.nii
    /usr/share/fsl/4.1/data/standard/MNI152_T1_1mm_brain.nii.gz

We can see that the image has been found in a local directory

Processing definition
---------------------

Now we need to define the processing step that will perform the diffusion
preprocessings.

::

    map_cluster_analysis_pipeline = MapClusterAnalysis()


It is possible to access the pipeline input specification.

::

    print(map_cluster_analysis_pipeline.get_input_spec())


Will return the input parameters the user can set:

.. code-block:: python

    INPUT SPECIFICATIONS

        map_image: ['String']
        thresh_size: ['Int']
        thresh_neg_bound: ['Tuple']
        thresh_pos_bound: ['Tuple']
        reference_image: ['File']
        target_image: ['File']
        anat_file: ['String']
        white_mesh_file: ['String']


We can now tune the pipeline parameters.
We first set the input dwi file:

::

    map_cluster_analysis_pipeline.map_image = wmap
    map_cluster_analysis_pipeline.thresh_size = 10
    map_cluster_analysis_pipeline.thresh_neg_bound = (-np.inf, -3)
    map_cluster_analysis_pipeline.thresh_pos_bound = (0.8, np.inf)
    map_cluster_analysis_pipeline.reference_image = reference
    """
    Study Configuration
    -------------------

    The pipeline is now set up and ready to be executed.
    For a complete description of a study execution, see the
    :ref:`Study Configuration description <study_configuration_guide>`

Study Configuration
-------------------

The pipeline is now set up and ready to be executed.
For a complete description of a study execution, see the
:ref:`Study Configuration description <study_configuration_guide>`

::

    brain_working_dir = os.path.join(working_dir, "brain")
    ensure_is_dir(brain_working_dir)
    default_config = SortedDictionary(
        ("output_directory", brain_working_dir),
        ("fsl_config", "/etc/fsl/4.1/fsl.sh"),
        ("use_fsl", True),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)
    study.run(map_cluster_analysis_pipeline)


Results
-------

Finally, we print the pipeline outputs

::

    print "\nOUTPUTS\n"
    for trait_name, trait_value in \
                    map_cluster_analysis_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)


.. note::
    Since only the motion and eddy corrections has been selected,
    the *unwrapped_phase_file* and *susceptibility_corrected_file*
    are not specified.
    Thus the *corrected_file* output contains the motion-eddy corrected
    image.

Vizualisation
-------------

::

    viewer_node = map_cluster_analysis_pipeline.nodes["mesh_cluster_rendering"]
    viewer_process = viewer_node.process
    for plug_name, plug in viewer_node.plugs.iteritems():
        if plug_name in ["nodes_activation", "selection_changed"]:
            continue
        # since it is a viewer node we normally have only inputs
        for (source_node_name, source_plug_name, source_node,
            source_plug, weak_link) in plug.links_from:

            source_plug_value = getattr(source_node.process,
                                        source_plug_name)
            source_trait = source_node.process.trait(source_plug_name)
            setattr(viewer_process, plug_name, source_plug_value)
    subprocess.Popen(viewer_process.get_commandline())

