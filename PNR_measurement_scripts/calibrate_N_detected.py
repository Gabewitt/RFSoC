import numpy as np
import receive_data_rfsoc as receiver
import matplotlib.pyplot as plt
from pathlib import Path
import time
from datetime import datetime
import os

import find_thresholds as threshold_finder
import PNR_analysis as pnr_analyzer


HOST = "0.0.0.0"
PORT = 65432
mu = 3

now = datetime.now()
day = now.strftime("%Y%m%d")
s_live = now.strftime("%H%M")

save_dir = Path.home() / "RFSoC" / "Data" / "calibration" / "detection_rates" / f"mu_{mu}" / f"{day}" / f"{s_live}"
save_dir.mkdir(parents=True, exist_ok=True)
filename_prefix = "detected_photon_rates_calibration"


data = receiver.receive_rates(
    host=HOST,
    port=PORT,

)


R_trigger = data[0][2]
R_detected = data[0][1]
N_detected = R_detected / R_trigger 

save_path = save_dir / f"{filename_prefix}_N_detected.csv"
np.savetxt(save_path, [N_detected], delimiter=",")
print(f"N_detected: {N_detected}")
print("Saved to:", save_path)