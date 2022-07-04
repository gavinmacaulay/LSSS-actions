# --- Begin generated header ---
import os
import sys
sys.path.append(os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + '/../../../../include'))
import lsss
# --- End generated header ---

import pandas as pd
from pathlib import Path
import time

projectDir = Path(r'C:\Users\gavin\OneDrive - Havforskningsinstituttet\Projects\2022 WindFarms')
dataDir = projectDir.joinpath('data')
saveDir = projectDir.joinpath('results')

df = pd.read_csv(dataDir.joinpath('Echograms to create.csv'))

for i, row in df.iterrows():
    start = pd.to_datetime(row['start_date'] + ' ' + row['start_utc'])
    stop = pd.to_datetime(row['stop_date'] + ' ' + row['stop_utc'])
    z = row['depth']
    
    print(f'Saving echogram from {start} to {stop} down to {z} m')
    
    # set echogram zoom
    p = '/lsss/module/PelagicEchogramModule/zoom/'
    limits = [{'time': start.isoformat() + 'Z', 'z': 0.0}, {'time': stop.isoformat() + 'Z', 'z': z}]
    lsss.post('/lsss/module/PelagicEchogramModule/zoom/', json=limits)
    
    lsss.get('/lsss/data/wait')
    
    time.sleep(5)

    p = {"save_dir": str(saveDir), 'figure_label': f'{i+1:02d}', 'image_dpi': 300}
    lsss.post('/lsss/package/Utilities/action/GetEchogram/run', json=p)
    
    lsss.get('/lsss/data/wait')
    
