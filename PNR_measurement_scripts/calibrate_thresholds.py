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
points_per_waveform = 16
amount_of_waveforms = 134217728 

now = datetime.now()
day = now.strftime("%Y%m%d")
s_live = now.strftime("%H%M")

save_dir = Path.home() / "RFSoC" / "Data" / "calibration" / "thresholds" / f"{day}" / f"{s_live}"
save_dir.mkdir(parents=True, exist_ok=True)
filename_prefix = "threshold_calibration"




data = receiver.receive_data(
        host=HOST,
        port=PORT,
        points_per_waveform=points_per_waveform,
        amount_of_waveforms=amount_of_waveforms
    )


waveforms, max_amplitudes = pnr_analyzer.classify(data)


thresholds = threshold_finder.interactive_find_thresholds(
            max_amplitudes,
            save_dir=save_dir,
            filename_prefix=filename_prefix
        )

np.save(save_dir / f"{filename_prefix}_thresholds.csv", thresholds)