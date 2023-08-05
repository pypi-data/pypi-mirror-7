.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

.. _example_caps.diffusion_estimation.py_tensor_estimation.pilot_second_order :

==================================
Second Order Tensor Estimation
==================================

.. hidden-code-block:: python
    :starthidden: True

    # The full use case code: caps.diffusion_estimation.py_tensor_estimation.pilot_second_order
    from caps.toy_datasets import get_sample_data
    from capsul.study_config import StudyConfig
    from capsul.utils.sorted_dictionary import SortedDictionary
    from nsap.lib.base import ensure_is_dir
    import os
    from caps.diffusion_preproc.bet import dBET
    from caps.diffusion_estimation.py_tensor_estimation import (
        SecondOrderTensorEstimation)
    working_dir = "/volatile/nsap/caps"
    fit_working_dir = os.path.join(working_dir, "diffusion_py_fit_second")
    ensure_is_dir(fit_working_dir)
    default_config = SortedDictionary(
        ("output_directory", fit_working_dir),
        ("fsl_config", "/etc/fsl/4.1/fsl.sh"),
        ("use_fsl", True),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)
    toy_dataset = get_sample_data("dwi")
    print(toy_dataset.dwi, toy_dataset.bvals, toy_dataset.bvecs)
    bet_pipeline = dBET()
    bet_pipeline.dw_image = toy_dataset.dwi
    bet_pipeline.bvals = toy_dataset.bvals
    study.run(bet_pipeline)
    fit_pipeline = SecondOrderTensorEstimation()
    print(fit_pipeline.get_input_spec())
    fit_pipeline.dwi_file = toy_dataset.dwi
    fit_pipeline.bvals_file = toy_dataset.bvals
    fit_pipeline.bvecs_file = toy_dataset.bvecs
    fit_pipeline.mask_file = bet_pipeline.bet_mask_file
    fit_pipeline.reference_file = bet_pipeline.outelements[0]
    fit_pipeline.select_fit = "ols"
    study.run(fit_pipeline)
    print("\nOUTPUTS\n")
    for trait_name, trait_value in fit_pipeline.get_outputs().iteritems():
        print("{0}: {1}".format(trait_name, trait_value))


.. link-to-block:: caps.diffusion_estimation.py_tensor_estimation.
                   SecondOrderTensorEstimation
    :label: API
    :right-side: True

.. topic:: Objective

    We propose here to estimate a second order tensor model from
    a diffusion sequence with two different strategies:

    1) the first strategy do not guarantee the positive definitness of
    the estimated tensors (we call this method OLS for Ordinary
    Least Square).

    2) the second one enables the estimation of semi-definite
    positive tensors (the quartic method).

Introduction
------------

Diffusion-Weighted Magnetic Resonance imaging (DW-MRI) provides a
unique probe to characterize the microstructure of materials.
DTI (Diffusion Tensor Imaging) measures the diffusion properties of
water molecules, and provides a physical description of the water
motion anisotropic behavior using a tensor representation. An excellent
introduction to DW-MRI is available in [1]_.

Diffusion tensors are usually estimated by solving this equation using
a standard :ref:`least squares procedure
<caps.diffusion_estimation.py_tensor_estimation.SecondOrderTensorEstimation>`.
Since this procedure does not guarantee the positive definiteness of
the tensors, negative eigenvalues are often set to an arbitrary small
positive value.

To overcome this limitation some authors directly estimate
positive-semi-definite tensors using a
:ref:`quartic decomposition with a non negative least quare procedure
<caps.diffusion_estimation.py_tensor_estimation.SecondOrderTensorEstimation>`.

Import
------

First we load the function that enables us to access the toy datasets:

::

    from caps.toy_datasets import get_sample_data


From capsul we then load the class to configure the study we want to
perform:

::

    from capsul.study_config import StudyConfig


Here two utility tools are loaded. The first one enables the creation
of ordered dictionary and the second ensure that a directory exists.
Note that the directory will be created if necessary.

::

    from capsul.utils.sorted_dictionary import SortedDictionary
    from nsap.lib.base import ensure_is_dir


We need some generic python modules:

::

    import os


From caps we need the pipeline that will enable use to estimate the
tensor model and the one necessary to extract the brain from a
diffusion sequence:

::

    from caps.diffusion_preproc.bet import dBET
    from caps.diffusion_estimation.py_tensor_estimation import (
        SecondOrderTensorEstimation)


Study Configuration
-------------------

For a complete description of a study configuration, see the
:ref:`Study Configuration description <study_configuration_guide>`

We first define the current working directory:

::

    working_dir = "/volatile/nsap/caps"
    fit_working_dir = os.path.join(working_dir, "diffusion_py_fit_second")
    ensure_is_dir(fit_working_dir)


And then define the study configuration:

::

    default_config = SortedDictionary(
        ("output_directory", fit_working_dir),
        ("fsl_config", "/etc/fsl/4.1/fsl.sh"),
        ("use_fsl", True),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)


Load the toy dataset
--------------------

We want to perform a second order tensor fit on a diffusion sequence data.
To do so, we use the *get_sample_data* function to load the
dataset:

.. seealso::

    For a complete description of the *get_sample_data* function, see the
    :ref:`Toy Datasets documentation <toy_datasets_guide>`

::

    toy_dataset = get_sample_data("dwi")


The *toy_dataset* is an Enum structure with some specific
elements of interest *dwi*, *bvals*, *bvecs* that contain the nifti
diffusion image ,the b-values and the b-vectors respectively.

::

    print(toy_dataset.dwi, toy_dataset.bvals, toy_dataset.bvecs)


Will return:

.. code-block:: python

    /home/ag239446/git/nsap-src/nsap/data/DTI30s010.nii
    /home/ag239446/git/nsap-src/nsap/data/DTI30s010.bval
    /home/ag239446/git/nsap-src/nsap/data/DTI30s010.bvec

We can see that the image has been found in a local directory

Processing definition
---------------------

Now we need to define the processing steps that will perform the tensor
fit. To do so, we first need to extract the brain mask based on the b=0
reference image. For a complete tutorial on how to use this pipeline,
see the :ref:`dBET Tutorial. <example_caps.diffusion_preproc.bet.pilot>`

::

    bet_pipeline = dBET()
    bet_pipeline.dw_image = toy_dataset.dwi
    bet_pipeline.bvals = toy_dataset.bvals
    study.run(bet_pipeline)


We then define the tensor fit processing step

::

    fit_pipeline = SecondOrderTensorEstimation()


It is possible to access the pipeline input specifications:

::

    print(fit_pipeline.get_input_spec())


Will return the input parameters the user can set:

.. code-block:: python

    INPUT SPECIFICATIONS

    dwi_file: ['File']
    bvals_file: ['File']
    bvecs_file: ['File']
    mask_file: ['File']

We can now tune the pipeline parameters.
We first set the input dwi informations:

::

    fit_pipeline.dwi_file = toy_dataset.dwi
    fit_pipeline.bvals_file = toy_dataset.bvals
    fit_pipeline.bvecs_file = toy_dataset.bvecs


And pipe the brain mask and reference image

::

    fit_pipeline.mask_file = bet_pipeline.bet_mask_file
    fit_pipeline.reference_file = bet_pipeline.outelements[0]


Before running the pipeline, you need to select the fitting method you
want to use.
The *ols* strategy is fast but estimated tensor may not be relevant.
The *quartic* strategy is quite slow but the expected diffusivity
coefficients are >=0.
In pratice, for good SNR, the difference is small in anatomical
structures.

::

    fit_pipeline.select_fit = "ols"


The pipeline is now ready to be run

::

    study.run(fit_pipeline)


Results
-------

Finally, we print the pipeline outputs

::

    print("\nOUTPUTS\n")
    for trait_name, trait_value in fit_pipeline.get_outputs().iteritems():
        print("{0}: {1}".format(trait_name, trait_value))


**References**

.. [1] Mori, S., 2007. Introduction to Diffusion Tensor Imaging.
       Elsevier.

