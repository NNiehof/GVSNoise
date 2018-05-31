# Nynke Niehof, 2018

from Experiment.genNoiseStim import genStim
from Experiment.GVS import GVS
import matplotlib.pyplot as plt


class TestGenStim(object):
    def __init__(self, f_samp):

        self.gen_stim = genStim(f_samp=f_samp)

    def test_noise(self, duration, amp):
        self.gen_stim.noise(duration, amp)
        self.stim_plot(self.gen_stim.stim, title="Noise")

    def test_fade(self, fade_samps):
        self.gen_stim.fade(fade_samps)
        self.stim_plot(self.gen_stim.stim, title="Noise with fade")

    def stim_plot(self, stim, title=""):
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
        gvs = GVS(max_voltage=3.0, logfile="testGenNoiseStimlog.log")
    except:
        return
    # white noise
    make_stim = genStim(f_samp)
    make_stim.noise(5.0, 3.0)
    samples = make_stim.stim
    gvs.write_to_channel(samples)

    # white noise with fade-in/fade-out
    make_stim.fade(f_samp * 1.0)
    samples = make_stim.stim
    gvs.write_to_channel(samples)
    gvs.quit()

if __name__ == "__main__":

    f_samp = 1e3

    # generate signal and send to GVS output channel
    test_noise_signal(f_samp)

    # plot generated signals
    test_stim = TestGenStim(f_samp)
    test_stim.test_noise(5.0, 3.0)
    test_stim.test_fade(f_samp * 0.5)
    plt.show()
