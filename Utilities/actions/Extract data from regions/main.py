# --- Begin generated header ---
import os
import sys
sys.path.append(os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + '/../../../../include'))
import lsss
# --- End generated header ---

import numpy as np
import matplotlib.pyplot as plt
from dateutil.parser import parse
from pathlib import Path

projectDir = Path(r'C:\Users\gavin\OneDrive - Aqualyd Limited\Documents\IMR working\Bottom calibration')
resultsDir = projectDir.joinpath('results')

# get list of selected regions
regions = lsss.get('/lsss/regions/region?selected=true&all=true')

# iterate over each region and get data for each ping
for r in regions:
    startPing = r['boundingBox'][0]['pingNumber']
    startDepth = r['boundingBox'][0]['z']
    endPing = r['boundingBox'][1]['pingNumber']
    endDepth = r['boundingBox'][1]['z']
    
    print(f'Processing region {r["id"]}')
    
    svData = {}
    alongshipAngle = {}
    athwartshipAngle = {}
    sample_range = {}
    ping_times = []
    ping_distance = []
    freqs = {}
    for ping in range(startPing, endPing+1):
        p = lsss.get(f'/lsss/data/ping?pingNumber={ping}&sv=true&angles=true&minDepth={startDepth}&maxDepth={endDepth}')
        print(ping)
        ping_times.append(parse(p['time']))
        ping_distance.append(p['vesselDistance'])
        if ping == startPing:
            for ch in p['channels']:
                svData[ch['id']] = []
                alongshipAngle[ch['id']] = []
                athwartshipAngle[ch['id']] = []
        for ch in p['channels']:
            chId = ch['id']
            freqs[chId] = ch['frequency'] # [Hz]
            svData[chId].append(ch['sv'])
            alongshipAngle[chId].append(ch['alongshipAngle'])
            athwartshipAngle[chId].append(ch['athwartshipAngle'])
            
    # convert to numpy arrays
    ping_times = np.asarray(ping_times)
    ping_distance = np.asarray(ping_distance) * 1.852 # [km]
    ping_distance -= ping_distance[0]

    for ch in p['channels']:
        chId = ch['id']
        svData[chId] = np.asarray(svData[chId])
        alongshipAngle[chId] = np.asarray(alongshipAngle[chId])
        athwartshipAngle[chId] = np.asarray(athwartshipAngle[chId])
        sample_range[chId] = np.linspace(startDepth, endDepth, num=svData[chId].shape[1])
    
    # do an echogram and phase plot
    for chId in svData.keys():
        fig, axs = plt.subplots(3, 1, sharex=True)
        im = axs[0].pcolormesh(ping_distance, sample_range[chId], svData[chId].T)
        cb = plt.colorbar(im, ax=axs[0])
        cb.set_label('S$_v$ re 1 m$^{-1}$ [dB]')
        im = axs[1].pcolormesh(ping_distance, sample_range[chId], alongshipAngle[chId].T)
        cb = plt.colorbar(im, ax=axs[1])
        cb.set_label('Angle [$\degree$]')
        im = axs[2].pcolormesh(ping_distance, sample_range[chId], athwartshipAngle[chId].T)
        cb = plt.colorbar(im, ax=axs[2])
        cb.set_label('Angle [$\degree$]')
        
        fig.supylabel('Depth [m]')
        fig.supxlabel('Distance [km]')
        for a in axs:
            a.invert_yaxis()

        site = 'unknown'
        transect = 'unknown'
        channel = ''
        
        figName = f'Transect_{ping_times[0].year}_site_{site}_transect_{transect}_channel_{channel}.png'
        fig.savefig(resultsDir.joinpath(figName), dpi=300, bbox_inches='tight', pad_inches=0.1)
    
    # extract phase angles at the bottom echo and produce some stats
    
    
    
    
    
