import numpy as np
import matplotlib.pyplot as plt
import csv
import os
from datetime import datetime
from scipy.stats import poisson
from scipy.signal import fftconvolve
import time
from scipy.signal import find_peaks 
import re
import math

import find_thresholds as threshold_finder



def extract_mu_from_txt(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    match = re.search(r"mu\s*=\s*([0-9.eE+-]+)", text)
    if match is None:
        raise ValueError("Could not find mu value in file.")

    return float(match.group(1))



def dps_to_individual_counts(dps_array, total_triggers=None, use_trigger_column=True):
    """
    Convert a dps_rate_measurement array of shape (N, 3):
        [threshold, cumulative_counts, trigger_counts]
    into individual photon counts.

    Parameters
    ----------
    dps_array : np.ndarray
        Array with columns:
        0 -> threshold
        1 -> cumulative counts (>=1, >=2, >=3, ...)
        2 -> trigger counts

    total_triggers : int or float, optional
        If provided, use this value directly.

    use_trigger_column : bool
        If True and total_triggers is None, use the first nonzero value
        found in column 2 as total_triggers.

    Returns
    -------
    thresholds : np.ndarray
        Thresholds corresponding to cumulative bins kept.

    cumulative_counts : np.ndarray
        Cleaned cumulative counts.

    individual_counts : np.ndarray
        Individual counts [0,1,2,...,last_tail] if total_triggers is known,
        otherwise [1,2,...,last_tail].
    """
    dps_array = np.asarray(dps_array)

    # Keep only rows with nonzero cumulative counts
    mask = dps_array[:, 1] > 0
    cleaned = dps_array[mask]

    thresholds = cleaned[:, 0]
    cumulative_counts = cleaned[:, 1]

    # Determine total triggers
    if total_triggers is None and use_trigger_column:
        trigger_vals = cleaned[:, 2][cleaned[:, 2] > 0]
        if len(trigger_vals) > 0:
            total_triggers = trigger_vals[0]

    # Convert cumulative -> individual
    individual_counts = cumulative_counts[:-1] - cumulative_counts[1:]
    individual_counts = np.append(individual_counts, cumulative_counts[-1])

    if total_triggers is not None:
        count_0 = total_triggers - cumulative_counts[0]
        individual_counts = np.insert(individual_counts, 0, count_0)


    ### Individual counts show the number of events with exactly 0, 1, 2, ... photons detected.
    return thresholds, cumulative_counts, individual_counts



def classify(data, chunk_size=16):
    waveforms = []
    max = []
    
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]

        waveforms.append(chunk)
        max.append(np.max(chunk))
    return waveforms, max


def classify_photon_number_max_ampltitude(data, thresholds):
    photon_number = []
    for waveform in data:
        m = np.max(waveform)
        photon_bin = np.searchsorted(thresholds, m, side='right')
        photon_number.append(photon_bin)
    return photon_number



def count_photon_numbers(photon_number_distribution):
    photon_number_distribution = np.asarray(photon_number_distribution, dtype=int)
    return np.bincount(photon_number_distribution)

def calculate_zero_photon_amount(measured_counts, N_detected):
    counts = measured_counts[1:]
    total_counts = np.sum(measured_counts)
    zero_photon_count = int((1 - N_detected) * total_counts / N_detected)
    counts = np.insert(counts, 0, zero_photon_count)
    return counts

def return_fraction_counts(R_detected):
    N_det = []
    for i in (R_detected):
        fraction = i/np.sum(R_detected)
        N_det.append(fraction)
    return N_det



def get_N_detected_from_max_amplitude_analysis(data, N_detected, thresholds):

    waveforms, max_amplitudes = classify(data)

    

    photon_numbers = classify_photon_number_max_ampltitude(waveforms, thresholds)

    photon_counts = count_photon_numbers(photon_numbers)
    photon_counts_with_zero = calculate_zero_photon_amount(photon_counts, N_detected=N_detected)
    N_detected_fraction = return_fraction_counts(photon_counts_with_zero)
    
    return N_detected_fraction, thresholds, photon_counts_with_zero






def save_analysis_results_csv(save_dir, N_detected_fraction, thresholds, photon_counts_with_zero):
    def to_1d_array(x):
        return np.atleast_1d(np.asarray(x, dtype=float))

    def fmt(x):
        return repr(float(x)) if x != "" else ""

    n_detected_csv_path = save_dir + "N_detected_fraction.csv"
    combined_csv_path = save_dir + "thresholds_and_photon_counts.csv"

    N_detected_fraction = to_1d_array(N_detected_fraction)
    thresholds = to_1d_array(thresholds)
    photon_counts_with_zero = to_1d_array(photon_counts_with_zero)

    with open(n_detected_csv_path, "w", newline="") as f:
        for val in N_detected_fraction:
            f.write(f"{fmt(val)}\n")

    max_len = max(len(N_detected_fraction), len(thresholds), len(photon_counts_with_zero))

    with open(combined_csv_path, "w", newline="") as f:
        f.write("label,N_detected_fraction,threshold,photon_count_with_zero\n")

        for i in range(max_len):
            label = str(i)
            frac = fmt(N_detected_fraction[i]) if i < len(N_detected_fraction) else ""
            thr = fmt(thresholds[i]) if i < len(thresholds) else ""
            cnt = fmt(photon_counts_with_zero[i]) if i < len(photon_counts_with_zero) else ""
            f.write(f"{label},{frac},{thr},{cnt}\n")

        sum_frac = fmt(np.sum(N_detected_fraction))
        sum_thr = fmt(np.sum(thresholds))
        sum_cnt = fmt(np.sum(photon_counts_with_zero))
        f.write(f"SUM,{sum_frac},{sum_thr},{sum_cnt}\n")

    print("Saved:", n_detected_csv_path)
    print("Saved:", combined_csv_path)