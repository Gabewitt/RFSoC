import shutil

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

    extract_photon_statistics = True
    save_data = True
    save_RAM_data = False

    now = datetime.now()
    day = now.strftime("%Y%m%d")
    s_live = now.strftime("%H%M")

    device_name = "Matterhorn"
    detector_name = "gN2a8-10"
    laser_name = "Pulsed_Laser_Source"
    mean_photon_number = 3
    measurement_type = "Signal_analysis"
    N_detected = 0.8260633261176761

    
    save_dir_data = "/home/rfsoc/Documents/SNSPD_Lab_Measurements/PNR/RFSoC/" + f"{day}/" 
    save_dir = "/home/rfsoc/Documents/SNSPD_Lab_Measurements/PNR/RFSoC/" + f"{day}/N_Detected_Fraction_Calibration_DDRam/" 

    if save_data:
        save_dir.mkdir(parents=True, exist_ok=True)
        print("Save directory:", save_dir)
        
    
    
    threshold_path = "/home/rfsoc/Documents/SNSPD_Lab_Measurements/PNR/RFSoC/" + f"{day}" + "/Threshold_Calibration_DDRam/threshold_calibration.csv"
    thresholds = np.loadtxt(threshold_path, delimiter=",")
    print("thresholds:", thresholds)
    
    N_detected_path = "/home/rfsoc/Documents/SNSPD_Lab_Measurements/PNR/RFSoC/" + f"{day}" + "/N_Detected_Fraction_Calibration/N_detected_DPS.csv"
    N_detected = np.loadtxt(N_detected_path, delimiter=",")
    print("N_detected:", N_detected)



    HOST = "0.0.0.0"
    PORT = 65432

    points_per_waveform = 16
    amount_of_waveforms = 10000000   # total waveforms you expect to receive

    data = receiver.receive_data(
        host=HOST,
        port=PORT,
        points_per_waveform=points_per_waveform,
        amount_of_waveforms=amount_of_waveforms
    )

    if save_RAM_data:
        save_path = save_dir_data / "received_data_RAM.npy"
        np.save(save_path, data)
        print("Saved to:", save_path)
    
    if extract_photon_statistics:
        N_detected_fraction, thresholds, photon_counts_with_zero = pnr_analyzer.get_N_detected_from_max_amplitude_analysis(data, N_detected=N_detected, thresholds=thresholds)
        
        save = pnr_analyzer.save_analysis_results_csv(save_dir, N_detected_fraction, thresholds, photon_counts_with_zero)


    
    server_path = f"/mnt/qtech-serv1/Projects/RFsoc/ZCU208B/Data/{day}/{device_name}/{detector_name}/{laser_name}/{mean_photon_number}/{s_live[11:13]}{s_live[14:16]}"
    os.makedirs(server_path, exist_ok=True)
    shutil.copytree(save_dir_data, server_path, dirs_exist_ok=True)
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