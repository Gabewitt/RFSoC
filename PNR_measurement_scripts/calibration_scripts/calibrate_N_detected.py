import numpy as np
import sys
import matplotlib.pyplot as plt
from pathlib import Path
import time
from datetime import datetime
import os

sys.path.append("/home/rfsoc/github/RFSoC/PNR_measurement_scripts/drivers")

import receive_data_rfsoc as receiver
import find_thresholds as threshold_finder
import PNR_analysis as pnr_analyzer

HOST = "0.0.0.0"
PORT = 65432


now = datetime.now()
day = now.strftime("%Y%m%d")
s_live = now.strftime("%H%M")



mean_photon_number = 1

save_dir = "/home/rfsoc/Documents/SNSPD_Lab_Measurements/PNR/RFSoC/" + f"{day}" + "/N_Detected_Fraction_Calibration/" + f"mu_{mean_photon_number}" + "/"
os.makedirs(save_dir, exist_ok=True)
filename_prefix = "N_detected_DPS"


data_location = "/mnt/qtech-serv1/Projects/RFsoc/ZCU208B/Data/20260319/Matterhorn/gN2a8-10/Pulsed_Laser_Source/1224/"+ f"mu_{mean_photon_number}" +"/dps_corrected_thresholds.csv"
print("Loading data from:", data_location)
data = np.loadtxt(data_location, delimiter=",", skiprows=1)
print(data)





R_trigger = data[0][2]
R_detected = data[0][1]
N_detected = R_detected / R_trigger 

print(f"R_trigger: {R_trigger}")
print(f"R_detected: {R_detected}")
print(f"N_detected: {N_detected}")

save_path = save_dir + f"{filename_prefix}.csv"
np.savetxt(save_path, [N_detected], delimiter=",")
print(f"N_detected: {N_detected}")
print("Saved to:", save_path)