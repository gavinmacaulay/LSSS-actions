# --- Begin generated header ---
import os
import sys
sys.path.append(os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + '/../../../../include'))
import lsss
# --- End generated header ---

# Idea is to use the selected region to calculate the 
# De Robertis & Higginbottom noise estimate as a function of 
# frequency and of vessel speed and produce a plot of this. 
# Also calculate the Range Detection Limit for a target of 
# a user-defined Sv level.

# TODO
# - cope with no selected regions
# - cope with multiple selected regions
# - Produce a plot of Sv as a function of depth and perhaps a Power_cal echogram
# - Allow the user to set bin size?
# - Allow user to set Sv level for RDL in the UI, and update in real-time the RDL result
# - Improve UI:
#   - table layout for results
#   - instructions (via Help?)

import tkinter as tk
import tkinter.ttk as ttk
import requests
import numpy as np

# Needs a region to be selected
d=requests.get(lsss.baseUrl + '/lsss/export/Sv')
# This is a CSV-formatted text, so pick out what we need...
d = d.text.split('\r\n')
d = np.genfromtxt(d, delimiter=',', skip_header=6, invalid_raise=False)
Sv = d[:,11:] # trim off non-Sv numbers
numPings, numSamples = np.shape(Sv)
regionHeight = d[0,7] - d[0,6] # [m]
mean_Sv = 10*np.log10(np.nanmean(np.power(10,Sv/10)))

# The selected region
regionId = lsss.get('/lsss/regions/selection')[0] # should only be one...
region = lsss.get('/lsss/regions/region/' + str(regionId) + '/mask')
regionPingStart = region[0]['pingNumber']
regionPingEnd = region[-1]['pingNumber']

# Get average vessel speed in the selected region.
# Needs the echogram plot module visible and showing only vessel speed.
speed = lsss.get('/lsss/module/EchogramPlotModule/data')
pingNums = np.array(speed['datasets'][0]['pingNumber'])
vesselSpeed = np.array(speed['datasets'][0]['vesselSpeed'])

# then use selected region ping range to select the speeds and calculate the average
i = np.where((pingNums >= regionPingStart) & (pingNums <= regionPingEnd))
regionSpeedMean = np.mean(vesselSpeed[i])
regionSpeedSTD = np.std(vesselSpeed[i])

# Get Numerical View data from a ping within the region. Needs numerical view turned on.
p = {'pingNumber':np.floor(np.mean([regionPingStart, regionPingEnd])), 'z': 0}
lsss.post('/lsss/module/PelagicEchogramModule/current-echogram-point', json=p)
ping = lsss.get('/lsss/module/NumericalViewModule/data') # for the selected ping
absorption = ping['channelData']['absorption']
frequency = ping['channelData']['frequency']

# Calculate the noise...
# assumes a rectangular region
r = np.linspace(d[0,6], d[0,7], num=Sv.shape[1])
tvg = 20*np.log10(r) + 2*absorption*r
power_cal = Sv - tvg

# take the mean across some bin size
M = 10 # samples to average over
N = 10 # pings to average over
rowId = np.floor((np.arange(0, np.shape(power_cal)[0])) / N).astype(int)
colId = np.floor((np.arange(0, np.shape(power_cal)[1])) / N).astype(int)
colID, rowID = np.meshgrid(colId, rowId)
compartmentID = (colID + rowID * np.amax(colId+1)).flatten()

power_cal_mean = 10*np.log10(np.bincount(compartmentID, weights=np.power(10, (power_cal.flatten()/10))/(M*N) ))
power_cal_mean = power_cal_mean.reshape(colId[-1]+1, rowId[-1]+1)
r_mean = np.linspace(r[0], r[-1], num=rowId[-1])

# take minimum in each depth bin
noise = np.amin(power_cal_mean, axis=1)
# and the mean across all min in the depth bins
noise_est = 10*np.log10(np.nanmean(np.power(10, noise/10)))

# Calculate the range detection limit
RDL_Sv = -80 # [dB]
r = np.arange(1.0, 2000.0) # [m]
noise_Sv = noise_est + 20*np.log10(r) + 2*absorption*r
RDL = r[np.where(noise_Sv <= RDL_Sv)[0][-1]]

# Show the results in a GUI
root = tk.Tk()
root.title('Background noise')

output = tk.Text(root, width=60, height=12)
output.configure(font=("Helvetica", 10))
output.pack(side='top', ipadx=5, ipady=5)

output.insert(tk.END, 'Noise calculated using De Robertis & Higginbottom method\n\n')
output.insert(tk.END, 'Frequency = {} kHz\n'.format(frequency/1e3))
output.insert(tk.END, 'Absorption = {:.4f} dB km\u207b\u00b9\n'.format(absorption*1e3))
output.insert(tk.END, 'Mean Sv = {:.1f} dB re 1 m\u207b\u00b9\n'.format(mean_Sv))
output.insert(tk.END, 'Mean vessel speed = {:.1f} knots (std = {:.1f})\n'.format(regionSpeedMean, regionSpeedSTD))

output.insert(tk.END, '\n')
output.insert(tk.END, 'Region is {} pings by {:.1f} m ({} samples)\n'.format(numPings, regionHeight, numSamples))
output.insert(tk.END, 'Bin size is {} samples by {} pings\n'.format(M, N))
output.insert(tk.END, 'Power_cal = {:.1f} dB\n'.format(noise_est))
output.insert(tk.END, 'RDL at Sv = {:.0f} dB is {:.0f} m'.format(RDL_Sv, RDL))

output.config(state='disabled')

ttk.Button(root, text='Close', command=root.destroy).pack(side='right')
ttk.Button(root, text='Help').pack(side='right')

root.mainloop()

