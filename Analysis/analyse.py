import numpy as np
import glob
import matplotlib.pyplot as plt
from readData import read_raw
import psychometricCurveFit as pcf


# load raw data in dataframe
data_folder = "D:/OneDrive/Code/GVSnoise/Data/pilot/Data"
f_paths = glob.glob("{}/*/*_GVSNoise_frame*.txt".format(data_folder))
df = read_raw(f_paths)

stim_range = np.arange(-6, 6, 0.5)
colours = ["red", "green", "blue", "orange"]

subjects = sorted(df["subject"].unique())
for sj in subjects:
    plt.figure()
    i_col = 0
    # get ratio of responses for each condition
    currents = sorted(df["current"].unique())
    frames = list(df["frameAngle"].unique())
    for frame in frames:
        for curr in currents:
            selection = df[(df["subject"] == sj) & (df["current"] == curr)
                           & (df["frameAngle"] == frame)]
            if len(selection) == 0:
                break
            stim = list(map(float, selection["rodAngle"]))
            resp = list(map(float, selection["response"]))
            xydata = pcf.success_ratio(stim, resp)
            psy, params = pcf.fit_sigmoid(xydata, xdata_range=stim_range)

            # plot the curve and data
            if i_col > len(colours):
                i_col = 0
            col = colours[i_col]
            i_col += 1
            stdev = 1 / params[1]
            plt.plot(stim_range, psy, lw=2.5, color=col,
                     label="{} mA, frame = {}, SD = {:.3f}".format(
                         curr, frame, stdev))
            plt.plot(xydata[0], xydata[1], "o", color=col)

        plt.xlim([-6, 6])
        plt.ylim([-0.05, 1.05])
        plt.xlabel("line angle")
        plt.ylabel("proportion CW responses")
        plt.title("subject {}".format(sj))
        plt.legend(loc="upper left")

plt.show()
