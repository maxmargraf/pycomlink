from __future__ import division
from collections import namedtuple
import numpy as np

from pycomlink.util.maintenance import deprecated


WetDryError = namedtuple('WetDryError', ('false_wet_rate',
                                         'missed_wet_rate',
                                         'matthews_correlation',
                                         'true_wet_rate',
                                         'true_dry_rate',
                                         'N_dry_reference',
                                         'N_wet_reference',
                                         'N_true_wet',
                                         'N_true_dry',
                                         'N_false_wet',
                                         'N_missed_wet',
                                         'N_all_pairs',
                                         'N_nan_pairs',
                                         'N_nan_reference_only',
                                         'N_nan_predicted_only'))

RainError = namedtuple('RainError', ['pearson_correlation',
                                     'coefficient_of_variation',
                                     'root_mean_square_error',
                                     'mean_absolute_error',
                                     'R_mean_reference',
                                     'R_mean_cml',
                                     'false_wet_rate',
                                     'missed_wet_rate',
                                     'false_wet_precipitation_rate',
                                     'missed_wet_precipitation_rate',
                                     'rainfall_threshold_wet',
                                     'N_all_pairs',
                                     'N_nan_pairs',
                                     'N_nan_reference_only',
                                     'N_nan_predicted_only'])


def calc_wet_dry_performance_metrics(reference, predicted):
    """

    Parameters
    ----------
    reference : boolean array-like
    predicted : boolean array-like

    Returns
    -------

    WetDryError : named tuple

    References
    -------
    https://en.wikipedia.org/wiki/Matthews_correlation_coefficient

    """

    assert reference.shape == predicted.shape


    # Remove values pairs if either one or both are NaN and calculate nan metrics
    nan_index = np.isnan(reference) | np.isnan(predicted)
    N_nan_pairs = nan_index.sum()
    N_all_pairs = len(reference)
    N_nan_reference_only = len(reference[nan_index])
    N_nan_predicted_only = len(predicted[nan_index])

    reference = reference[~nan_index]
    predicted = predicted[~nan_index]

    assert reference.shape == predicted.shape

    # Calculate N_tp, tn, N_fp, N_fn, N_wet_reference (real positive cases) and N_dry_reference (real negative cases)

    # N_tp is number of true positive wet event (true wet)
    N_tp = ((reference == True) & (predicted == True)).sum()

    # N_tn is number of true negative wet event (true dry)
    N_tn = ((reference == False) & (predicted == False)).sum()

    # N_fp is number of false positive wet event (false wet)
    N_fp = ((reference == False) & (predicted == True)).sum()

    # N_fn is number of false negative wet event  (missed wet)
    N_fn = ((reference == True) & (predicted == False)).sum()

    N_wet_reference = (reference == True).sum()
    N_dry_reference = (reference == False).sum()


    # Then calculate all the metrics
    true_wet_rate = N_tp / N_wet_reference
    true_dry_rate = N_tn / N_dry_reference
    false_wet_rate = N_fp / N_dry_reference
    missed_wet_rate = N_fn / N_wet_reference

    matthews_correlation = (N_tp*N_tn-N_fp+N_fn) / np.sqrt((N_tp+N_fp)*(N_tp+N_fn)*(N_tn+N_fp)*(N_tn+N_fn))

    return WetDryError(false_wet_rate=false_wet_rate,
                       missed_wet_rate=missed_wet_rate,
                       matthews_correlation=matthews_correlation,
                       true_wet_rate=true_wet_rate,
                       true_dry_rate=true_dry_rate,
                       N_dry_reference=N_dry_reference,
                       N_wet_reference=N_wet_reference,
                       N_true_wet=N_tp,
                       N_true_dry=N_tn,
                       N_false_wet=N_fp,
                       N_missed_wet=N_fn,
                       N_all_pairs=N_all_pairs,
                       N_nan_pairs=N_nan_pairs,
                       N_nan_reference_only=N_nan_reference_only,
                       N_nan_predicted_only=N_nan_predicted_only)


def calc_rain_error_performance_metrics(reference, predicted, rainfall_threshold_wet=None):
    """

    Parameters
    ----------
    reference : float array-like
    predicted : float array-like
    rainfall_threshold_wet : float (optional)
    threshold separating wet/rain and dry/non-rain periods

    Returns
    -------

    RainError : named tuple

    References
    -------
    https://en.wikipedia.org/wiki/Matthews_correlation_coefficient
    https://github.com/scikit-learn/scikit-learn/blob/7389dba/sklearn/metrics/regression.py#L184
    https://github.com/scikit-learn/scikit-learn/blob/7389dba/sklearn/metrics/regression.py#L112
    Overeem et al. 2013: www.pnas.org/cgi/doi/10.1073/pnas.1217961110

        """

    assert reference.shape == predicted.shape

    # Remove values pairs if either one or both are NaN and calculate nan metrics
    nan_index = np.isnan(reference) | np.isnan(predicted)
    N_nan_pairs = nan_index.sum()
    N_all_pairs = len(reference)
    N_nan_reference_only = len(reference[nan_index])
    N_nan_predicted_only = len(predicted[nan_index])

    reference = reference[~nan_index]
    predicted = predicted[~nan_index]

    assert reference.shape == predicted.shape

    # threshold separating wet/rain and dry/non-rain periods
    if rainfall_threshold_wet is None:
        rainfall_threshold_wet = 0.1


    # calculate performance metrics: pcc, cv, rmse and mae
    pearson_correlation = np.corrcoef(reference, predicted)
    coefficient_of_variation = np.std(predicted)/np.std(reference) - np.mean(reference)
    root_mean_square_error = np.sqrt(np.mean((predicted-reference)**2))
    mean_absolute_error = (np.average(predicted-reference)).mean()

    # calculate the precipitation sums of reference and predicted time series
    R_mean_reference = reference.sum()
    R_mean_cml = predicted.sum()

    # calculate false and missed wet rates and the precipitation at these times
    N_false_wet = ((reference < rainfall_threshold_wet) & (predicted >= rainfall_threshold_wet)).sum()
    N_dry = (reference < rainfall_threshold_wet).sum()
    false_wet_rate = N_false_wet / float(N_dry)

    N_missed_wet = ((reference >= rainfall_threshold_wet) & (predicted < rainfall_threshold_wet)).sum()
    N_wet = (reference >= rainfall_threshold_wet).sum()
    missed_wet_rate = N_missed_wet / float(N_wet)

    false_wet_precipitation_rate = predicted[(reference < rainfall_threshold_wet) &
                                             (predicted >= rainfall_threshold_wet)].sum()

    missed_wet_precipitation_rate = predicted[(reference >= rainfall_threshold_wet) &
                                              (predicted < rainfall_threshold_wet)].sum()


    return RainError(pearson_correlation = pearson_correlation[0,1],
                     coefficient_of_variation = coefficient_of_variation,
                     root_mean_square_error = root_mean_square_error,
                     mean_absolute_error = mean_absolute_error,
                     R_mean_reference = R_mean_reference,
                     R_mean_cml = R_mean_cml,
                     false_wet_rate = false_wet_rate,
                     missed_wet_rate = missed_wet_rate,
                     false_wet_precipitation_rate = false_wet_precipitation_rate,
                     missed_wet_precipitation_rate = missed_wet_precipitation_rate,
                     rainfall_threshold_wet = rainfall_threshold_wet,
                     N_all_pairs = N_all_pairs,
                     N_nan_pairs = N_nan_pairs,
                     N_nan_reference_only = N_nan_reference_only,
                     N_nan_predicted_only = N_nan_predicted_only)


@deprecated('Please use `calc_wet_dry_performance_metrics()`')
def calc_wet_error_rates(df_wet_truth, df_wet):
    N_false_wet = ((df_wet_truth == False) & (df_wet == True)).sum()
    N_dry = (df_wet_truth == False).sum()
    false_wet_rate = N_false_wet / float(N_dry)

    N_missed_wet = ((df_wet_truth == True) & (df_wet == False)).sum()
    N_wet = (df_wet_truth == True).sum()
    missed_wet_rate = N_missed_wet / float(N_wet)

    return WetError(false=false_wet_rate, missed=missed_wet_rate)

