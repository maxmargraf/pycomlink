import unittest
import numpy as np
import collections
import pycomlink as pycml


class TestWetDryandRainErrorfunctions(unittest.TestCase):
    def test_WetDryError_with_simple_arrays(self):
        reference = np.array([True, False, True, True, False,
                              True, False, np.nan, np.nan, np.nan])
        predicted = np.array([True, False, False, True, True,
                              True, True, True, False, np.nan])

        wd_error = pycml.validation.stats.calc_wet_dry_performance_metrics(
            reference,
            predicted)

        class_name = 'WetDryError_reference'
        fields = 'false_wet_rate missed_wet_rate matthews_correlation ' \
                 'true_wet_rate true_dry_rate N_dry_reference N_wet_reference '\
                 'N_true_wet N_true_dry N_false_wet N_missed_wet ' \
                 'N_all_pairs N_nan_pairs N_nan_reference_only ' \
                 'N_nan_predicted_only'
        WetDryError_reference = collections.namedtuple(class_name, fields)
        ref = WetDryError_reference(0.66666667, 0.25, 0.182574185835055, 0.75,
                                    0.33333334, 3, 4, 3, 1, 2, 1, 10, 3, 3, 1)

        np.testing.assert_array_almost_equal(
            wd_error,
            ref)

    def test_RainError_with_simple_arrays(self):
        reference = np.array([1, 0, 1, 1, 0, 1, 0, np.nan, np.nan, np.nan])
        predicted = np.array([1, 0, 0, 1, 1, 0.01, 1, 1, 0, np.nan])

        rainerror = pycml.validation.stats.calc_rain_error_performance_metrics(
            reference,
            predicted,
            rainfall_threshold_wet=0.1)

        class_name = 'RainError_reference'
        fields = 'pearson_correlation coefficient_of_variation ' \
                 'root_mean_square_error mean_absolute_error R_sum_reference ' \
                 'R_sum_predicted R_mean_reference R_mean_predicted ' \
                 'false_wet_rate missed_wet_rate ' \
                 'false_wet_precipitation_rate missed_wet_precipitation_rate ' \
                 'rainfall_threshold_wet N_all_pairs N_nan_pairs ' \
                 'N_nan_reference_only N_nan_predicted_only'
        RainError_reference = collections.namedtuple(class_name, fields)
        ref = RainError_reference(-0.164712494, 1.319578531, 0.754046228,
                                  0.570000000, 4, 4.01, 0.571428571,
                                  0.572857142, 0.666666667, 0.666666666,
                                  1, 1, 0.1, 10, 3, 3, 1)

        np.testing.assert_almost_equal(
            rainerror,
            ref)

        # Test that the calculation does not change the input arrays
        np.testing.assert_almost_equal(
            reference,
            np.array([1, 0, 1, 1, 0, 1, 0, np.nan, np.nan, np.nan]))

        np.testing.assert_almost_equal(
            predicted,
            np.array([1, 0, 0, 1, 1, 0.01, 1, 1, 0, np.nan]))
