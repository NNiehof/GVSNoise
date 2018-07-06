import numpy as np
import glob
import matplotlib.pyplot as plt
from readData import read_raw
import psychometricCurveFit as pcf


# load raw data in dataframe
data_folder = "D:/OneDrive/Code/GVSnoise/Data/pilot/Data"
f_paths = glob.glob("{}/*/*_GVSNoise_*.txt".format(data_folder))
df = read_raw(f_paths)

plt.figure()
stim_range = np.arange(-10, 10, 0.5)
colours = ["red", "green", "blue", "orange"]
i_col = 0

subjects = df["subject"].unique()
for sj in subjects:
    # get ratio of responses for each condition
    currents = df["current"].unique()
    for curr in currents:
        selection = df[(df["subject"] == sj) & (df["current"] == curr)]
        stim = list(map(float, selection["rodAngle"]))
        resp = list(map(float, selection["response"]))
        xydata = pcf.success_ratio(stim, resp)
        psy, params = pcf.fit_sigmoid(xydata, xdata_range=stim_range)

        # plot the curve and data
        if i_col > len(colours):
            i_col = 0
        col = colours[i_col]
        i_col += 1
        plt.plot(stim_range, psy, lw=2.5, color=col,
                 label="{} mA".format(curr))
        plt.plot(xydata[0], xydata[1], "o", color=col)
        plt.xlim([-10, 10])
        plt.ylim([-0.05, 1.05])
        plt.xlabel("line angle")
        plt.ylabel("proportion CW responses")
        plt.legend()

plt.show()
