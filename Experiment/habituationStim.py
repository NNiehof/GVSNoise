# Nynke Niehof, 2018

from Experiment.GVS import GVS
from Experiment.genNoiseStim import genStim
import matplotlib.pyplot as plt


def habituation_signal():
    """
    Generate a habituation signal with a slow ramp
    """
    amp = 1.0
    duration = 25.0
    f_samp = 1e3
    buffer_size = int(duration * f_samp)
    gvs = GVS(max_voltage=amp)
    timing = {"rate": f_samp, "samps_per_chan": buffer_size}
    connected = gvs.connect("cDAQ1Mod1/ao0", **timing)
    if connected:
        # white noise with fade-in/fade-out
        make_stim = genStim(f_samp)
        make_stim.noise(25.0, amp)
        make_stim.fade(f_samp * 10.0)
        faded_samples = make_stim.stim
        print("start galvanic stim")
        gvs.write_to_channel(faded_samples)
        print("end galvanic stim")
    gvs.quit()
    return faded_samples


def stimulus_plot(stim, title=""):
    plt.figure()
    plt.plot(stim)
    plt.xlabel("sample")
    plt.ylabel("amplitude (mA)")
    plt.title(title)


if __name__ == "__main__":
    faded_stim = habituation_signal()
    stimulus_plot(faded_stim, title="white noise with fade in/out")
    plt.show()

