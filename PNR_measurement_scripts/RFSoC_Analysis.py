import numpy as np
import receive_data_rfsoc as receiver
import matplotlib.pyplot as plt
from pathlib import Path
import time
from datetime import datetime
import os

import find_thresholds as threshold_finder
import PNR_analysis as pnr_analyzer

def main():

    extract_photon_statistics = False
    manual_thresholds = [10250, 11780]
    optimise_thresholds = True
    save_data = True
    save_RAM_data = False

    now = datetime.now()
    day = now.strftime("%Y%m%d")
    s_live = now.strftime("%H%M")

    device_name = "Matterhorn"
    detector_name = "gN2a8-10"
    laser_name = "Pulsed_Laser_Source"
    mean_photon_number = 2
    measurement_type = "Signal_analysis"
    N_detected = 0.8260633261176761

    
    save_dir = (
        Path.home()
        / "RFSoC"
        / "Data"
        / day
        / device_name
        / detector_name
        / laser_name
        / f"mu_{mean_photon_number}"
        / s_live
        / measurement_type
        
        )

    if save_data:
        save_dir.mkdir(parents=True, exist_ok=True)
        print("Save directory:", save_dir)




    HOST = "0.0.0.0"
    PORT = 65432

    points_per_waveform = 16
    amount_of_waveforms = 134217728   # total waveforms you expect to receive

    data = receiver.receive_data(
        host=HOST,
        port=PORT,
        points_per_waveform=points_per_waveform,
        amount_of_waveforms=amount_of_waveforms
    )

    if save_RAM_data:
        save_path = save_dir / "received_data_RAM.npy"
        np.save(save_path, data)
        print("Saved to:", save_path)
    
    if extract_photon_statistics:
        N_detected_fraction, thresholds, photon_counts_with_zero = pnr_analyzer.get_N_detected_from_max_amplitude_analysis(data, N_detected=N_detected, save_dir=save_dir, filename_prefix="max_amplitude_threshold_search", manual_thresholds=manual_thresholds, threhold_finder=optimise_thresholds )
        save = pnr_analyzer.save_analysis_results_csv(save_dir, N_detected_fraction, thresholds, photon_counts_with_zero)


    return data



if __name__ == "__main__":
    data = main()
    print("Final data length:", len(data))

    plt.plot(data[:200])
    plt.show()
    x, y = pnr_analyzer.classify(data)
    plt.figure(dpi=500)
    plt.hist(y, bins=2000)
    plt.show()