# Nynke Niehof, 2018

from __future__ import division

import numpy as np
from GVS import GVS


class genStim(object):
    def __init__(self, f_samp=1e3):
        """
        Class to create single-channel noise stimuli.

        :param f_samp: sampling frequency (Hz)
        """

        self.f_samp = f_samp
        self.n_samp = 0.0
        self.stim = None

    def noise(self, duration, amp, bandwidth=(-np.inf, np.inf)):
        """
        Generate noise from random samples on the interval
        Unif[-amplitude, amplitude)

        :param duration: signal duration (seconds)
        :param amp: maximum signal amplitude
        :param bandwidth: (tuple )bandwidth limits (Hz)
        :return:
        """
        self.n_samp = int(duration * self.f_samp)
        self.stim = (2 * amp) * np.random.random(size=self.n_samp) - amp

    def fade(self, fade_samples):
        fader = np.ones(self.n_samp)
        samp = np.arange(0, self.n_samp)
        ramp = np.square(np.sin(0.5 * np.pi * samp / self.n_samp))
        # fade in
        fader[0:self.n_samp] = ramp
        # fade out
        fader[(len(fader) - self.n_samp):] = ramp[::-1]
        # apply the fades
        self.stim = self.stim * fader

