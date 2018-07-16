import os
import json
import numpy as np
from psychopy import visual, core, event
from Experiment.GVS import GVS
from Experiment.genNoiseStim import GenStim

"""
Quickly test the effect of GVS on line orientation for
individual calibration purposes.
"""

# constants
f_sampling = 1e3
n_trials = 10
duration_s = 8.0
fade_s = 2.0
current_mA = 1.0
stochastic_gvs = True
physical_channel_name = "cDAQ1Mod1/ao0"


def quit_program():
    win.close()
    core.quit()


# root directory
abs_path = os.path.abspath("__file__")
root_dir = os.path.dirname(os.path.dirname(abs_path))
settings_dir = "{}/Settings".format(root_dir)

# window and display settings
display_file = "{}/display.json".format(settings_dir)
with open(display_file) as json_file:
    win_settings = json.load(json_file)
win = visual.Window(**win_settings)

# line stimulus
line = visual.Line(win=win, start=(0,-200), end=(0, 200), lineWidth=6,
                   lineColor=(-0.84, -0.84, -0.84))
start_text = visual.TextStim(win=win, text="press SPACE to start trial",
                             pos=(0.0, 0.0), color=(-1, -1, 0.6), units="pix",
                             height=40)

# GVS setup
buffer_size = int(duration_s * f_sampling)
timing = {"rate": f_sampling, "samps_per_chan": buffer_size}
gvs = GVS()
gvs.connect(physical_channel_name, **timing)

# create and send GVS signals
make_stim = GenStim(f_sampling)
for trial in range(n_trials):
    if stochastic_gvs:
        make_stim.noise(duration_s, current_mA)
    else:
        # positive current for even trials, negative current for uneven trials
        if (trial % 2) == 0:
            direction = 1
        else:
            direction = -1
        make_stim.stim = np.ones(int(duration_s * f_sampling))
        make_stim.stim = make_stim.stim * current_mA * direction
        make_stim.n_samp = len(make_stim.stim)
    make_stim.fade(fade_s * f_sampling)

    # wait for space bar press to start trial
    start_text.draw()
    win.flip()
    key_presses = []
    while not key_presses:
        key_presses = event.getKeys(keyList=["space", "escape"])
        event.clearEvents(eventType="mouse")
        if "space" in key_presses:
            pass
        elif "escape" in key_presses:
            quit_program()

    # display line
    line.draw()
    win.flip()

    # send GVS signal to stimulator
    gvs.write_to_channel(make_stim.stim, reset_to_zero_volts=True)

quit_program()
