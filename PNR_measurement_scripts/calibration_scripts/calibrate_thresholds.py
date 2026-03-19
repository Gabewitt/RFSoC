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
points_per_waveform = 16
amount_of_waveforms = 10000000 

mean_photon_number = 3

now = datetime.now()
day = now.strftime("%Y%m%d")
s_live = now.strftime("%H%M")

save_dir = "/home/rfsoc/Documents/SNSPD_Lab_Measurements/PNR/RFSoC/" + f"{day}" + "/Threshold_Calibration_DDRam/"

os.makedirs(save_dir, exist_ok=True)
filename_prefix = "threshold_calibration"

data_dir = "/home/rfsoc/Documents/SNSPD_Lab_Measurements/PNR/RFSoC/20260319/received_data_RAM_3.npy"
data = np.load(data_dir)
print("Data loaded from:", data_dir[:10])


"""
data = receiver.receive_data(
        host=HOST,
        port=PORT,
        points_per_waveform=points_per_waveform,
        amount_of_waveforms=amount_of_waveforms
    )
"""

waveforms, max_amplitudes = pnr_analyzer.classify(data)


thresholds = threshold_finder.interactive_find_thresholds(
            max_amplitudes,
            save_dir=save_dir,
            filename_prefix=filename_prefix
        )

np.savetxt(save_dir + f"{filename_prefix}.csv", thresholds, delimiter=",")
