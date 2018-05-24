# Nynke Niehof, 2018

from Experiment.genNoiseStim import genStim
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
        plt.show()


if __name__ == "__main__":

    f_samp = 1e3
    test_stim = TestGenStim(f_samp)
    test_stim.test_noise(10.0, 3.0)
    test_stim.test_fade(f_samp * 0.5)
