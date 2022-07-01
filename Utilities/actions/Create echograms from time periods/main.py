# --- Begin generated header ---
import os
import sys
sys.path.append(os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + '/../../../../include'))
import lsss
# --- End generated header ---

import pandas as pd
from pathlib import Path

sys.path.append("../GetEchogram")
from main import getEchogram

projectDir = Path(r'C:\Users\gavin\OneDrive - Havforskningsinstituttet\Projects\2022 WindFarms')
dataDir = projectDir.joinpath('data')
saveDir = projectDir.joinpath('results')

df = pd.read_csv(dataDir.joinpath('Echograms to create.csv'))

for i, row in df.iterrows():
    start = pd.to_datetime(row['start_date'] + ' ' + row['start_utc'])
    stop = pd.to_datetime(row['stop_date'] + ' ' + row['stop_utc'])
    z = row['depth']
    
    print(start, stop, z)
    
    # set echogram zoom
    p = '/lsss/module/PelagicEchogramModule/zoom/'
    limits = [{'time': start.isoformat() + 'Z', 'z': 0.0}, {'time': stop.isoformat() + 'Z', 'z': z}]
    lsss.post('/lsss/module/PelagicEchogramModule/zoom/', json=limits)
    
    lsss.get('/lsss/data/wait')

    saveEchogram(saveDir, figure_label=f'{i+1:02d}', image_dpi=300)
