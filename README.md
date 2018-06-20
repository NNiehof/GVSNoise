# GVS Noise

## Goal
GVSNoise is an experiment program that communicates with a NIDAQmx digital-to-analog converter to send stochastic current stimuli
to a Biopac stimulator. The stimulator sends currents though a cathodal and an anodal electrode lead. The electrodes are attached
to the mastoid processes behind the ears of a human subject, in order to electrically stimulate the vestibular nerves through the
skull. The goal is to make the vestibular neural signal noisy, and thus less reliable, to investigate how a change in sensory
reliability influences visuovestibular integration. This is studied with a rod-and-frame task, in which participants judge
the orientation of a line presented inside a titled square frame. Stimuli are generated with the PsychoPy package for Python 3.6.

## Usage
Start the experiment by Experiment/running main.py. The experiment can be modified by editing files in the Settings folder.
Display settings for the PsychoPy window can be specified in display.json, PsychoPy stimuli can be set in stimuli.json.

Stimuli must be specified in the form as in this example:  
```
"myStim": {
		"stimType": "Rect",
		"settings": {
			"width": 300.0,
			"height": 300.0,
			"pos": [
				0,
				0
			],
			"lineWidth": 5,
			"lineColor": [
				-0.8,
				-0.8,
				-0.8
			],
			"fillColor": null,
			"ori": 0.0,
			"units": "pix"
		}
	}
```
The value for "stimType" must be an existing PsychoPy stimulus class (e.g. Line, Circle, Rect, ...). Under "settings",
specify the arguments of the stimulus, see PsychoPy documentation http://www.psychopy.org/api/visual.html  

Data and log files will be saved in a folder with the participant number, in the Data and Log directories, respectively.