.. CAPS AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

.. _example_caps.quality_assurance.fmri.pilot :

    
.. hidden-code-block:: python
    :starthidden: True

    # The full use case code: caps.quality_assurance.fmri.pilot
    # Pilot imports
    from caps.toy_datasets import get_sample_data

    # Get toy dataset
    toy_dataset = get_sample_data("localizer")
    print toy_dataset.fmri, toy_dataset.TR

    array = load_fmri_dataset(toy_dataset.fmri)
    print array.shape
    signal = get_fmri_signal(array)
    print signal.shape
    #tfn = get_fmri_temporal_fluctuation_noise(array)
    #print tfn.shape

    (average_intensity, polynomial, residuals, fluctuation,
     drift) = get_snr_percent_fluctuation_and_drift(array)
    spectrum = get_residuals_spectrum(residuals, 2.4 * 10e-3)
    spectrum_figure(spectrum)
    time_series_figure(average_intensity, polynomial)

    (fluctuations, theoretical_fluctuations,
     rdc) = get_weisskoff_analysis(array, max_size=21)
    print fluctuations
    #weisskoff_figure(fluctuations, theoretical_fluctuations, rdc)
    plt.show()


::

    # Pilot imports
    from caps.toy_datasets import get_sample_data

    # Get toy dataset
    toy_dataset = get_sample_data("localizer")
    print toy_dataset.fmri, toy_dataset.TR

    array = load_fmri_dataset(toy_dataset.fmri)
    print array.shape
    signal = get_fmri_signal(array)
    print signal.shape
    #tfn = get_fmri_temporal_fluctuation_noise(array)
    #print tfn.shape

    (average_intensity, polynomial, residuals, fluctuation,
     drift) = get_snr_percent_fluctuation_and_drift(array)
    spectrum = get_residuals_spectrum(residuals, 2.4 * 10e-3)
    spectrum_figure(spectrum)
    time_series_figure(average_intensity, polynomial)

    (fluctuations, theoretical_fluctuations,
     rdc) = get_weisskoff_analysis(array, max_size=21)
    print fluctuations
    #weisskoff_figure(fluctuations, theoretical_fluctuations, rdc)
    plt.show()

