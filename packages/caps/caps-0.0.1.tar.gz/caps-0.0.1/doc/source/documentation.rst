.. raw:: html

  <div class="container-index">

Documentation of the CApsul PipelineS
======================================

dMRI
----

.. raw:: html

  <!-- Block section -->

    <div class="row-fluid">

      <div class="span6 box">
        <h2><a href="generated/diffusion_preproc/index.html">
            Diffusion MRI preprocessings
        </a></h2>
        <blockquote>
            This pipeline enbables preprocessings of diffusion MRI images:
            <ul>
             <li>Distortion correction</li>
             <li>Tensor Estimation</li>
             <li>dMRI registration</li>
             <li>Scalar Map computation</li>
            </ul>
        </blockquote>
      </div>

      <div class="span6 box">
        <h2><a href="generated/diffusion_estimation/index.html">
          Diffusion MRI model estimation
        </a></h2>
        <blockquote>
          This set of pipelines enables the estimation of diffusion models:
          <ul>
           <li>Tensor model: least square</li>
           <li>Tensor model: quartics non negative least square</li>
          </ul>
        </blockquote>
      </div>

    </div>

    <div class="row-fluid">

      <div class="span6 box">
        <h2><a href="generated/diffusion_registration/index.html">
          Diffusion MRI model registration
        </a></h2>
        <blockquote>
          This set of pipelines enables the registration of diffusion tensor
          models:
          <ul>
           <li>Registration: Non linear anatomical registration</li>
           <li>Reorientation: Finite Strain or PPD</li>
          </ul>
        </blockquote>
      </div>

    </div>

    </div>

fMRI
----

.. raw:: html

  <!-- Block section -->

    <div class="row-fluid">

      <div class="span6 box">
        <h2><a href="generated/functional_connectivity/index.html">
            fMRI functional connectivity
        </a></h2>
        <blockquote>
            This pipeline enbables the functional connectivity analysis of fMRI
            datasets.
        </blockquote>
      </div>

      <div class="span6 box">
        <h2><a href="generated/preclinic_functional/index.html">
          fMRI preclinic pipeline
        </a></h2>
        <blockquote>
          This pipeline enables the preprossings  and statistical analysis
          of preclinic functional images with SPM and FSL.
          The different steps involved are:
          <ul>
           <li>Reorientation</li>
           <li>Slice registration</li>
           <li>Slice timing</li>
           <li>Realignement</li>
           <li>Coregistration</li>
           <li>Segmentation/Registration to a template space</li>
           <li>Normalization (resampling)</li>
           <li>Smoothing</li>
           <li>Brain extraction</li>
           <li>First level analysis</li>
          </ul>
        </blockquote>
      </div>

    </div>

    <div class="row-fluid">

      <div class="span6 box">
        <h2><a href="generated/functional_preproc/index.html">
          fMRI preprocessings pipeline
        </a></h2>
        <blockquote>
          This pipeline enables the preprossings of preclinic functional images
          with PyPreProcess (SPM).
          The different steps involved are:
          <ul>
           <li>Slice timing</li>
           <li>Realignement</li>
           <li>Coregistration</li>
           <li>Segmentation/Registration to a template space</li>
           <li>Normalization (resampling)</li>
           <li>Smoothing</li>
           <li>Brain extraction</li>
          </ul>
        </blockquote>
      </div>

    </div>


Misc
----

.. raw:: html

  <!-- Block section -->

    <div class="row-fluid">

      <div class="span6 box">
        <h2><a href="generated/dicom_converter/index.html">
            DICOM converter pipeline
        </a></h2>
        <blockquote>
            This pipeline enbables the NIFTI conversion and the 
            anonymization of DICOM files. Moreover, it is possible to
            transcode the patient name.
        </blockquote>
      </div>

      <div class="span6 box">
        <h2><a href="generated/utils/index.html">
            Utility
        </a></h2>
        <blockquote>
            A set of pipelines that are shared with others.
        </blockquote>
      </div>

    </div>

    <div class="row-fluid">

      <div class="span6 box">
        <h2><a href="generated/quality_control/index.html">
            Quality control pipeline
        </a></h2>
        <blockquote>
            A set of pipelines to check the quality of a result.
        </blockquote>
      </div>

      <div class="span6 box">
        <h2><a href="generated/quality_assurance/index.html">
            Quality assurance pipeline
        </a></h2>
        <blockquote>
            A set of pipelines to check the quality of the input images.
        </blockquote>
      </div>
    </div>



