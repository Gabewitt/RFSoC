import matplotlib.pyplot as plt
import numpy as np
import os
from scipy.signal import find_peaks


def valley_thresholds_from_hist_data(data, bins=2000, peak_prominence=100, peak_distance=20):
    counts, bin_edges = np.histogram(data, bins=bins)
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])

    peaks, _ = find_peaks(counts, prominence=peak_prominence, distance=peak_distance)

    valley_indices = []
    valley_x = []

    for i in range(len(peaks) - 1):
        left = peaks[i]
        right = peaks[i + 1]

        local_min_idx = np.argmin(counts[left:right + 1]) + left
        valley_indices.append(local_min_idx)
        valley_x.append(bin_centers[local_min_idx])

    return counts, bin_edges, bin_centers, peaks, valley_indices, valley_x


def plot_histogram_with_peaks_and_valleys(
    data,
    counts,
    bin_centers,
    peaks,
    valley_indices,
    valley_x,
    save_path=None,
    title="Max amplitude histogram",
    manual_thresholds=None
):
    plt.figure(figsize=(10, 6))
    plt.hist(data, bins=len(counts), alpha=0.7, label="Histogram")

    if len(peaks) > 0:
        plt.plot(bin_centers[peaks], counts[peaks], "ro", label="Peaks")

    if len(valley_indices) > 0:
        plt.plot(bin_centers[valley_indices], counts[valley_indices], "go", label="Valleys")

    for i, x in enumerate(valley_x):
        label = "Detected thresholds" if i == 0 else None
        plt.axvline(x=x, color="green", linestyle="--", alpha=0.7, label=label)

    if manual_thresholds is not None:
        for i, x in enumerate(manual_thresholds):
            label = "Manual thresholds" if i == 0 else None
            plt.axvline(x=x, color="blue", linestyle=":", alpha=0.8, label=label)

    plt.xlabel("Max amplitude")
    plt.ylabel("Counts")
    plt.title(title)
    plt.legend()

    if save_path is not None:
        plt.savefig(save_path, dpi=500, bbox_inches="tight")

    plt.show()


def parse_manual_thresholds(text):
    """
    Convert input like '100, 200, 350.5' into a list of floats.
    Empty input returns [].
    """
    text = text.strip()
    if text == "":
        return []

    return [float(x.strip()) for x in text.split(",") if x.strip() != ""]


def interactive_find_thresholds(
    data,
    save_dir=None,
    filename_prefix="threshold_search",
    initial_bins=2000,
    initial_peak_prominence=200,
    initial_peak_distance=80
):
    bins = initial_bins
    peak_prominence = initial_peak_prominence
    peak_distance = initial_peak_distance
    manual_thresholds = []

    while True:
        counts, bin_edges, bin_centers, peaks, valley_indices, valley_x = valley_thresholds_from_hist_data(
            data,
            bins=bins,
            peak_prominence=peak_prominence,
            peak_distance=peak_distance
        )

        detected_thresholds = np.array(valley_x, dtype=float)

        final_thresholds = np.sort(
            np.concatenate([detected_thresholds, np.array(manual_thresholds, dtype=float)])
        ) if len(manual_thresholds) > 0 else np.sort(detected_thresholds)

        save_path = None
        if save_dir is not None:
            os.makedirs(save_dir, exist_ok=True)
            save_path = os.path.join(save_dir, f"{filename_prefix}.png")

        print("\n--- Current settings ---")
        print(f"bins = {bins}")
        print(f"peak_prominence = {peak_prominence}")
        print(f"peak_distance = {peak_distance}")
        print(f"Detected peak x positions: {bin_centers[peaks]}")
        print(f"Detected valley thresholds: {detected_thresholds}")
        print(f"Manual thresholds: {manual_thresholds}")
        print(f"Final thresholds: {final_thresholds}")

        plot_histogram_with_peaks_and_valleys(
            data,
            counts,
            bin_centers,
            peaks,
            valley_indices,
            valley_x,
            save_path=save_path,
            title="Max amplitude histogram with peaks and valleys",
            manual_thresholds=manual_thresholds
        )

        happy = input("\nAre you happy with these thresholds? [y/n]: ").strip().lower()

        if happy == "y":
            
            return final_thresholds

        change_params = input("Do you want to change bins / peak_prominence / peak_distance? [y/n]: ").strip().lower()
        if change_params == "y":
            new_bins = input(f"bins [{bins}]: ").strip()
            new_peak_prominence = input(f"peak_prominence [{peak_prominence}]: ").strip()
            new_peak_distance = input(f"peak_distance [{peak_distance}]: ").strip()

            if new_bins != "":
                bins = int(new_bins)
            if new_peak_prominence != "":
                peak_prominence = float(new_peak_prominence)
            if new_peak_distance != "":
                peak_distance = int(new_peak_distance)

        add_manual = input("Do you want to replace manual thresholds? [y/n]: ").strip().lower()
        if add_manual == "y":
            manual_text = input("Enter manual thresholds separated by commas: ")
            manual_thresholds = parse_manual_thresholds(manual_text)