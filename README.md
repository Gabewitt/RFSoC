# This repo holds the analysis code for analyzing and classifying snspd data recorded using the RFSoC using Max amplitude discrimination



## How to use (I think)

**PNR_measurement_scripts/calibration_scripts/Receive_Data.py** is used to receive the data once in the ram. This saves the data in the raw .npy format.

**PNR_measurement_scripts/calibration_scripts/calibrate_thresholds.py** is used to calibrate the thresholds. Plots the distributions and you insert the thresholds and it reruns until you are satisfied.

**PNR_measurement_scripts_scripts/RFSoC_Analysis.py**, should be the file to run the PNR. Takes in the list of thresholds + data from ram. Loads in the npy file, and the thresholds. It outputs the fraction of each count.




There are three different folders inside this repo that contain specific things.

### Calibration Scripts

This folder contains calibrate_thresholds.py which takes in the data from the RFSoC (in our case it would be the waveforms from the RAM), then after getting the max amplitude of all the pulses go through a threshod finding scripts where the code finds the valeys/minimum point between two histogram peaks. You can change the parameters of this search if the results are not great, you can also manualy add where valleys are located. This returns an array of thresholds used to classify the max amplitudes of the data.

calibrate_N_detected gives the fraction of detected photons from the DPS method (using the rfsoc's internal counting counts above a threshold logic).

### Drivers

The driver file holds the different function to operate all the analysis.

### RFSoC_Analysis.py

this .py is the main analysis where you give the data from the ram and the thresholds and the code returns the fractions of the counts depending on the set N_detected. It calculates the number of 0 photon counts, and then measures the fractions of each counts.

### PNR_POVM

this it the POVM fitting code where you can use the fractions from rfsoc_analysis.py to put in this povm analysis 



### Saving

everything should save on the server under:

RFsoc/ZCU208B/Data/{day}/{device_name}/{detector_name}/{laser_name}/mu_{mean_photon_number}/{s_live[11:13]}{s_live[14:16]}
