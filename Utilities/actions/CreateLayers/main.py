# --- Begin generated header ---
import os
import sys
sys.path.append(os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + '/../../../../include'))
import lsss
# --- End generated header ---

from pathlib import Path
import csv

projectDir = Path(r'C:\Users\gavin\OneDrive - Aqualyd Limited\Documents\Aqualyd\Projects\2021-05 SIO ORH survey analysis')
metaDataFile = projectDir.joinpath(r'Data\Metadata_selected_transects_generated.csv')

# Generate a vertical divider at the start and end of each transect

with open(metaDataFile) as csv_file:
    csv_reader = csv.DictReader(csv_file, delimiter=',')
    for row in csv_reader:
        # load in transects start and end times
        vert_divider_at = [row['start_time'].replace(' ', 'T') + 'Z', row['end_time'].replace(' ', 'T') + 'Z']
        for v in vert_divider_at:
            print(f'Creating vertical divider at {v}')
            echogramPoint = {"time": v, "z": 800.0}
            lsss.post('/lsss/module/PelagicEchogramModule/vertical-divider', json=echogramPoint)
