# Nynke Niehof, 2018

import matplotlib.pyplot as plt
from sys import path
from os.path import dirname

path.append(dirname(path[0]))
from Experiment.genNoiseStim import genStim
from Experiment.GVS import GVS


class TestGenStim(object):
    def __init__(self, f_samp):

        self.gen_stim = genStim(f_samp=f_samp)

    def test_noise(self, duration, amp):
        self.gen_stim.noise(duration, amp)
        self.stim_plot(self.gen_stim.stim, title="Noise")

    def test_fade(self, fade_samps):
        self.gen_stim.fade(fade_samps)
        self.stim_plot(self.gen_stim.stim, title="Noise with fade")


def stim_plot(stim, title=""):
    plt.figure()
    plt.plot(stim)
    plt.xlabel("sample")
    plt.ylabel("amplitude (mA)")
    plt.title(title)


def test_noise_signal(f_samp):
    """
    Generate a white noise signal and a white noise with a fade-in and fade-out.
    Check the generated voltage with an oscilloscope.
    """
    try:
        gvs = GVS(max_voltage=1.0, logfile="testGenNoiseStimlog.log")
        gvs.connect(physical_channel_name="cDAQ1Mod1/ao0")
    except:
        return
    # white noise
    make_stim = genStim(f_samp)
    make_stim.noise(40.0, 0.3)
    samples = make_stim.stim
    # gvs.write_to_channel(samples)

    # white noise with fade-in/fade-out
    make_stim.fade(f_samp * 10.0)
    faded_samples = make_stim.stim
    print("start galvanic stim")
    gvs.write_to_channel(faded_samples)
    print("end galvanic stim")
    gvs.quit()

    return samples, faded_samples

if __name__ == "__main__":

    f_samp = 1e3

    # generate signal and send to GVS output channel
    stim, faded_stim = test_noise_signal(f_samp)

    # plot generated signals
    stim_plot(stim, title="white noise")
    stim_plot(faded_stim, title="white noise with fade in/out")
    plt.show()
